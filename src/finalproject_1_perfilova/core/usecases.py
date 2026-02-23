from datetime import datetime

from finalproject_1_perfilova.core.models import User, Portfolio
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