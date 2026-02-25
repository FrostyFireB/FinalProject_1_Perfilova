import argparse

from finalproject_1_perfilova.logging_config import setup_logging

from finalproject_1_perfilova.core.usecases import (
    register_user,
    login_user,
    show_portfolio,
    buy,
    sell,
    get_rate,
)

from finalproject_1_perfilova.core.exceptions import (
    InsufficientFundsError,
    CurrencyNotFoundError,
    ApiRequestError,
    WalletNotFoundError,
)

from finalproject_1_perfilova.parser_service.api_clients import CoinGeckoClient, ExchangeRateApiClient
from finalproject_1_perfilova.parser_service.config import get_config
from finalproject_1_perfilova.parser_service.storage import RatesStorage
from finalproject_1_perfilova.parser_service.updater import RatesUpdater
from finalproject_1_perfilova.parser_service.scheduler import RatesScheduler

from finalproject_1_perfilova.infra.database import DatabaseManager


def main():
    setup_logging()

    parser = argparse.ArgumentParser(prog="project")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # register
    p_reg = subparsers.add_parser("register")
    p_reg.add_argument("--username", required=True)
    p_reg.add_argument("--password", required=True)

    # login
    p_login = subparsers.add_parser("login")
    p_login.add_argument("--username", required=True)
    p_login.add_argument("--password", required=True)

    # show-portfolio
    p_show = subparsers.add_parser("show-portfolio")
    p_show.add_argument("--base", default="USD")

    # buy
    p_buy = subparsers.add_parser("buy")
    p_buy.add_argument("--currency", required=True)
    p_buy.add_argument("--amount", required=True, type=float)

    # sell
    p_sell = subparsers.add_parser("sell")
    p_sell.add_argument("--currency", required=True)
    p_sell.add_argument("--amount", required=True, type=float)

    # get-rate
    p_rate = subparsers.add_parser("get-rate")
    p_rate.add_argument("--from", dest="from_cur", required=True)
    p_rate.add_argument("--to", dest="to_cur", required=True)

    # update-rates
    p_upd = subparsers.add_parser("update-rates")
    p_upd.add_argument(
        "--source",
        choices=("coingecko", "exchangerate", "all"),
        default="all",
    )

    # scheduler
    p_sched = subparsers.add_parser("scheduler")
    p_sched.add_argument("--interval", type=int, default=300)
    p_sched.add_argument(
        "--source",
        choices=["coingecko", "exchangerate", "all"],
        default="all",
    )

    # show-rates
    p_show_rates = subparsers.add_parser("show-rates")
    p_show_rates.add_argument("--currency", required=False)
    p_show_rates.add_argument("--top", required=False, type=int)
    p_show_rates.add_argument("--base", default="USD")

    args = parser.parse_args()

    try:
        if args.command == "register":
            user = register_user(args.username, args.password)
            print(
                f"Пользователь '{user.username}' зарегистрирован (id={user.user_id})."
                f"Войдите: login --username {user.username} --password ****"
            )

        elif args.command == "login":
            user = login_user(args.username, args.password)
            print(f"Вы вошли как '{user.username}'")

        elif args.command == "show-portfolio":
            print(show_portfolio(args.base))

        elif args.command == "buy":
            print(buy(args.currency, args.amount))

        elif args.command == "sell":
            print(sell(args.currency, args.amount))

        elif args.command == "get-rate":
            rate, updated_at = get_rate(args.from_cur, args.to_cur)
            print(
                f"Курс {args.from_cur.upper()}->{args.to_cur.upper()}: "
                f"{rate:.8f} (обновлено: {updated_at})"
            )
            print(
                f"Обратный курс {args.to_cur.upper()}-{args.from_cur.upper()}: "
                f"{(1.0 / rate):.8e}"
            )

        elif args.command == "update-rates":
            cfg = get_config()
            storage = RatesStorage(cfg.RATES_FILE_PATH, cfg.HISTORY_FILE_PATH)

            clients = []
            if args.source in ("coingecko", "all"):
                clients.append(CoinGeckoClient(cfg=cfg))
            if args.source in ("exchangerate", "all"):
                clients.append(ExchangeRateApiClient(cfg=cfg))

            updater = RatesUpdater(clients=clients, storage=storage)

            total = updater.run_update()
            print(f"Обновление завершено. Всего обновлено курсов: {total}.")

        elif args.command == "scheduler":
            cfg = get_config()
            storage = RatesStorage(cfg.RATES_FILE_PATH, cfg.HISTORY_FILE_PATH)

            clients = []
            if args.source in ("coingecko", "all"):
                clients.append(CoinGeckoClient(cfg=cfg))
            if args.source in ("exchangerate", "all"):
                clients.append(ExchangeRateApiClient(cfg=cfg))

            updater = RatesUpdater(clients=clients, storage=storage)
            scheduler = RatesScheduler(updater)

            print(
                f"Планировщик запущен (interval={args.interval} сек, source={args.source}). "
                f"Ctrl+C для остановки."
            )
            scheduler.run_forever(interval_seconds=args.interval)

        elif args.command == "show-rates":
            db = DatabaseManager()
            snap = db.read("rates.json", None)

            if not snap or not isinstance(snap, dict) or "pairs" not in snap:
                print("Локальный кэш курсов пуст. Выполните 'update-rates', чтобы загрузить данные.")
                return

            pairs = snap.get("pairs", {})
            last_refresh = snap.get("last_refresh", "-")

            base = (args.base or "USD").strip().upper()

            if base != "USD":
                base_pair = f"{base}_USD"
                if base_pair not in pairs:
                    print(f"База '{base}' недоступна: нет пары {base_pair} в кэше. Сначала обновите курсы.")
                    return
                base_usd = float(pairs[base_pair]["rate"])
                if base_usd == 0:
                    print(f"База '{base}' недоступна: некорректный курс {base_pair}.")
                    return

            rows = []
            for pair, info in pairs.items():
                rate = float(info["rate"])
                updated_at = info.get("updated_at", "-")
                source = info.get("source", "-")

                frm, to = pair.split("_", 1)

                if to != "USD":
                    continue

                if args.currency:
                    cur = args.currency.strip().upper()
                    if frm != cur:
                        continue

                if base == "USD":
                    shown_pair = f"{frm}_USD"
                    shown_rate = rate
                else:
                    shown_pair = f"{frm}_{base}"
                    shown_rate = rate / base_usd

                rows.append((shown_pair, shown_rate, source, updated_at))

            if not rows:
                if args.currency:
                    print(f"Курс для '{args.currency.strip().upper()}' не найден в кэше.")
                else:
                    print("В кэше нет подходящих курсов.")
                return

            if args.top:
                rows.sort(key=lambda x: x[1], reverse=True)
                rows = rows[: args.top]
            else:
                rows.sort(key=lambda x: x[0])

            print(f"Курсы (last_refresh={last_refresh}, base={base}):")
            for pair, r, source, updated_at in rows:
                print(f"- {pair}: {r:.6f} (source={source}, updated_at={updated_at})")

    except InsufficientFundsError as e:
        print(str(e))

    except WalletNotFoundError as e:
        print(str(e))

    except CurrencyNotFoundError as e:
        print(str(e))
        print("Подсказка: используйте get-rate или проверьте код валюты (USD, EUR, RUB, BTC, ETH).")

    except ApiRequestError as e:
        print(str(e))
        print("Подсказка: повторите попытку позже или проверьте подключение к интернету.")

    except Exception as e:
        print(str(e))