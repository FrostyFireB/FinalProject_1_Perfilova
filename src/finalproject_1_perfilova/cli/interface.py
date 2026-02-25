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
    p_upd.add_argument("--source", choices=["coingecko", "exchangerate"], required=False)

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
                f"{(1.0 / rate):.2f}"
            )

        elif args.command == "update-rates":
            cfg = get_config()

            clients = []
            if args.source in (None, "coingecko"):
                clients.append(CoinGeckoClient())
            if args.source in (None, "exchangerate"):
                clients.append(ExchangeRateApiClient())

            storage = RatesStorage(cfg.RATES_FILE_PATH, cfg.HISTORY_FILE_PATH)
            updater = RatesUpdater(clients, storage)

            total = updater.run_update()
            print(f"Обновление завершено. Всего обновлено курсов: {total}.")

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