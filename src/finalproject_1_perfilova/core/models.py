from __future__ import annotations

import hashlib
import secrets
from datetime import datetime

class User:
    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str,
        salt: str,
        registration_date: datetime,
    ):
        self._user_id = int(user_id)
        self.username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @property
    def registration_date(self):
        return self._registration_date

    @username.setter
    def username(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Имя не может быть пустым.")
        self._username = value.strip()
        
    def get_user_info(self):
        return f"id={self._user_id}, username='{self._username}', registered_at={self._registration_date.isoformat()}"

    def change_password(self, new_password: str):
        if not isinstance(new_password, str) or len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов.")
        self._hashed_password = self._make_hash(new_password, self._salt)

    def verify_password(self, password: str):
        return self._hashed_password == self._make_hash(password, self._salt)

    @staticmethod
    def _make_hash(password: str, salt: str):
        raw = (password + salt).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @classmethod
    def create_new(cls, user_id: int, username: str, password: str):
        if not isinstance(password, str) or len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов.")
        salt = secrets.token_hex(8)
        hashed = cls._make_hash(password, salt)
        return cls(
            user_id=user_id,
            username=username,
            hashed_password=hashed,
            salt=salt,
            registration_date=datetime.now(),
        )

    def to_dict(self):
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat(timespec="seconds"),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            user_id=int(data["user_id"]),
            username=str(data["username"]),
            hashed_password=str(data["hashed_password"]),
            salt=str(data["salt"]),
            registration_date=datetime.fromisoformat(data["registration_date"]),
        )

class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self.balance = balance
    
    @property
    def currency_code(self):
        return self._currency_code
    
    @currency_code.setter
    def currency_code(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("currency_code не может быть пустым.")
        self._currency_code = value.strip().upper()

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("Баланс должен быть числом.")
        value = float(value)
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным.")
        self._balance = value

    def deposit(self, amount: float):
        if not isinstance(amount, (int, float)) or float(amount) <= 0:
            raise ValueError("amount должен быть > 0.")
        self.balance = self.balance + float(amount)

    def withdraw(self, amount: float):
        if not isinstance(amount, (int, float)) or float(amount) <= 0:
            raise ValueError("amount должен быть > 0.")
        amount = float(amount)
        if amount > self.balance:
            raise ValueError("Недостаточно средств.")
        self.balance = self.balance - amount

    def get_balance_info(self):
        return f"{self._currency_code}: {self._balance:.4f}"

class Portfolio:
    def __init__(self, user_id: int, wallets: dict[str, Wallet] | None = None):
        self._user_id = int(user_id)
        self._wallets: dict[str, Wallet] = wallets or {}

    @property
    def user_id(self):
        return self._user_id

    @property
    def wallets(self) -> dict[str, Wallet]:
        return dict(self._wallets)

    def add_currency(self, currency_code: str):
        code = currency_code.strip().upper()
        if not code:
            raise ValueError("currency_code не может быть пустым.")
        if code in self._wallets:
            raise ValueError(f"Кошелёк {code} уже существует.")
        self._wallets[code] = Wallet(code, 0.0)

    def get_wallet(self, currency_code: str):
        code = currency_code.strip().upper()
        if code not in self._wallets:
            raise ValueError(f"Кошелёк {code} не найден.")
        return self._wallets[code]

    def to_dict(self) -> dict:
        return {
            "user_id": self._user_id,
            "wallets": {code: {"balance": w.balance} for code, w in self._wallets.items()},
        }

    @classmethod
    def from_dict(cls, data: dict):
        wallets_raw = data.get("wallets", {})
        wallets = {code: Wallet(code, float(w.get("balance", 0.0))) for code, w in wallets_raw.items()}
        return cls(user_id=int(data["user_id"]), wallets=wallets)