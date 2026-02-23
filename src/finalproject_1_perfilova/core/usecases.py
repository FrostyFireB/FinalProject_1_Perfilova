from datetime import datetime

from finalproject_1_perfilova.core.models import User, Portfolio, Wallet
from finalproject_1_perfilova.core.utils import read_json, write_json


USERS_FILE = "users.json"
PORTFOLIOS_FILE = "portfolios.json"
SESSION_FILE = "session.json"


def _next_user_id(users: list[dict]):
    if not users:
        return 1
    max_id = 0
    for u in users:
        if int(u["user_id"]) > max_id:
            max_id = int(u["user_id"])
    return max_id + 1


def register_user(username: str, password: str):
    users = read_json(USERS_FILE, [])
    for u in users:
        if u["username"] == username:
            raise ValueError(f"Имя пользователя '{username}' уже занято")
    
    user_id = _next_user_id(users)
    
    user = User.create_new(user_id=user_id, username=username, password=password)
    
    users.append(user.to_dict())
    write_json(USERS_FILE, users)

    portfolios = read_json(PORTFOLIOS_FILE, [])
    portfolios.append(Portfolio(user_id=user.user_id, wallets={}).to_dict())
    write_json(PORTFOLIOS_FILE, portfolios)

    return user


def login_user(username: str, password: str):
    users = read_json(USERS_FILE, [])

    found = None
    for u in users:
        if u["username"] == username:
            found = u
            break

    if found is None:
        raise ValueError(f"Пользователь '{username}' не найден")

    user = User.from_dict(found)

    if not user.verify_password(password):
        raise ValueError("Неверный пароль")

    session = {
        "user_id": user.user_id,
        "username": user.username,
        "logged_in_at": datetime.now().isoformat(timespec="seconds"),
    }
    write_json(SESSION_FILE, session)

    return user


def get_session():
    session = read_json(SESSION_FILE, None)
    return session


def require_login():
    session = get_session()
    if not session:
        raise ValueError("Сначала выполните login")
    return session


def _validate_currency(code: str):
    if not isinstance(code, str) or not code.strip():
        raise ValueError("currency_code не может быть пустой строкой.")
    return code.strip().upper()


def _validate_amount(amount):
    if not isinstance(amount, (int, float)):
        raise ValueError("'amount' должен быть положительным числом")
    amount = float(amount)
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    return amount


def load_portfolio(user_id: int):
    portfolios = read_json(PORTFOLIOS_FILE, [])
    for p in portfolios:
        if int(p["user_id"]) == int(user_id):
            return Portfolio.from_dict(p)
    return Portfolio(user_id=user_id, wallets={})


def save_portfolio(portfolio: Portfolio):
    portfolios = read_json(PORTFOLIOS_FILE, [])
    updated = False
    for i in range(len(portfolios)):
        if int(portfolios[i]["user_id"]) == int(portfolio.user_id):
            portfolios[i] = portfolio.to_dict()
            updated = True
            break
    if not updated:
        portfolios.append(portfolio.to_dict())
    write_json(PORTFOLIOS_FILE, portfolios)


def get_rate(from_currency: str, to_currency: str):
    frm = _validate_currency(from_currency)
    to = _validate_currency(to_currency)

    rates = read_json("rates.json", {})
    pair = f"{frm}_{to}"
    rev_pair = f"{to}_{frm}"

    # прямой курс
    if pair in rates and isinstance(rates[pair], dict):
        rate = float(rates[pair]["rate"])
        updated_at = str(rates[pair]["updated_at"])
        return rate, updated_at

    # обратный курс (если есть BTC_USD, то USD_BTC = 1 / BTC_USD)
    if rev_pair in rates and isinstance(rates[rev_pair], dict):
        rev_rate = float(rates[rev_pair]["rate"])
        if rev_rate == 0:
            raise ValueError(f"Курс {frm}-{to} недоступен. Повторите попытку позже.")
        rate = 1.0 / rev_rate
        updated_at = str(rates[rev_pair]["updated_at"])
        return rate, updated_at

    raise ValueError(f"Не удалось получить курс для {frm}-{to}")


def show_portfolio(base: str = "USD"):
    session = require_login()
    base_cur = _validate_currency(base)

    user_id = int(session["user_id"])
    username = session["username"]
    portfolio = load_portfolio(user_id)

    if not portfolio.wallets:
        return f"Портфель пользователя '{username}' пуст."

    lines = []
    lines.append(f"Портфель пользователя '{username}' (база: {base_cur}):")

    total = 0.0
    for code, wallet in portfolio.wallets.items():
        bal = wallet.balance

        if code == base_cur:
            value = bal
        else:
            rate, _ts = get_rate(code, base_cur)
            value = bal * rate

        total += value
        lines.append(f"- {code}: {bal:.4f} -> {value:.2f} {base_cur}")

    lines.append("-" * 30)
    lines.append(f"ИТОГО: {total:,.2f} {base_cur}")
    return "\n".join(lines)


def buy(currency: str, amount: float, base: str = "USD"):
    session = require_login()
    cur = _validate_currency(currency)
    base_cur = _validate_currency(base)
    amount = _validate_amount(amount)

    user_id = int(session["user_id"])
    portfolio = load_portfolio(user_id)

    # если кошелька нет — нужно создать
    if cur not in portfolio.wallets:
        portfolio.add_currency(cur)

    wallet = portfolio.get_wallet(cur)
    before = wallet.balance
    wallet.deposit(amount)
    after = wallet.balance

    rate, _ts = get_rate(cur, base_cur)
    cost = amount * rate

    save_portfolio(portfolio)

    return (
        f"Покупка выполнена: {amount:.4f} {cur} по курсу {rate:.2f} {base_cur}/{cur}\n"
        f"Изменения в портфеле:\n"
        f"- {cur}: было {before:.4f} -> стало {after:.4f}\n"
        f"Оценочная стоимость покупки: {cost:,.2f} {base_cur}"
    )


def sell(currency: str, amount: float, base: str = "USD"):
    session = require_login()
    cur = _validate_currency(currency)
    base_cur = _validate_currency(base)
    amount = _validate_amount(amount)

    user_id = int(session["user_id"])
    portfolio = load_portfolio(user_id)

    if cur not in portfolio.wallets:
        raise ValueError(
            f"У вас нет кошелька '{cur}'. Добавьте валюту: она создаётся автоматически при первой покупке."
        )

    wallet = portfolio.get_wallet(cur)
    before = wallet.balance

    if amount > before:
        raise ValueError(f"Недостаточно средств: доступно {before:.4f} {cur}, требуется {amount:.4f} {cur}")

    wallet.withdraw(amount)
    after = wallet.balance

    rate, _ts = get_rate(cur, base_cur)
    revenue = amount * rate

    save_portfolio(portfolio)

    return (
        f"Продажа выполнена: {amount:.4f} {cur} по курсу {rate:.2f} {base_cur}/{cur}\n"
        f"Изменения в портфеле:\n"
        f"- {cur}: было {before:.4f} -> стало {after:.4f}\n"
        f"Оценочная выручка: {revenue:,.2f} {base_cur}"
    )