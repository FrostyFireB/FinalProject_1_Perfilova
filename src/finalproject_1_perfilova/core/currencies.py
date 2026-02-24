from abc import ABC, abstractmethod
from finalproject_1_perfilova.core.exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("name не может быть пустой строкой.")
        self._name = value.strip()

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value: str):
        if not isinstance(value, str):
            raise ValueError("code должен быть строкой.")
        code = value.strip().upper()

        if not (2 <= len(code) <= 5) or " " in code:
            raise ValueError("code должен быть 2-5 символов, верхний регистр, без пробелов.")
        self._code = code

    @abstractmethod
    def get_display_info(self):
        pass


class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name=name, code=code)
        self.issuing_country = issuing_country

    @property
    def issuing_country(self):
        return self._issuing_country

    @issuing_country.setter
    def issuing_country(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("issuing_country не может быть пустой строкой.")
        self._issuing_country = value.strip()

    def get_display_info(self):
        return f"{self.name} ({self.code}), {self.issuing_country}"


class CryptoCurrency(Currency):
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float):
        super().__init__(name=name, code=code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("algorithm не может быть пустой строкой.")
        self._algorithm = value.strip()

    @property
    def market_cap(self):
        return self._market_cap

    @market_cap.setter
    def market_cap(self, value: float):
        if not isinstance(value, (int, float)):
            raise ValueError("market_cap должен быть числом.")
        value = float(value)
        if value < 0:
            raise ValueError("market_cap не может быть отрицательным.")
        self._market_cap = value

    def get_display_info(self):
        return f"{self.name} ({self.code}), algo={self.algorithm}, cap={self.market_cap:.2f}"


# Минимальный список поддерживаемых валют
_SUPPORTED = {
    "USD": FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
    "RUB": FiatCurrency("Russian Ruble", "RUB", "Russia"),
    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 0.0),
    "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 0.0),
}


def get_currency(code: str):
    """
    Возвращает объект Currency по коду.
    Если код неизвестен — бросает CurrencyNotFoundError.
    """
    if not isinstance(code, str) or not code.strip():
        raise CurrencyNotFoundError("Код валюты не может быть пустым")

    c = code.strip().upper()
    if c not in _SUPPORTED:
        raise CurrencyNotFoundError(f"Неизвестная валюта '{c}'")
    return _SUPPORTED[c]
