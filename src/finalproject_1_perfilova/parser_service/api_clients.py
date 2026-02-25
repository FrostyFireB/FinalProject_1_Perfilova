import requests
from abc import ABC, abstractmethod

from finalproject_1_perfilova.core.exceptions import ApiRequestError
from finalproject_1_perfilova.parser_service.config import get_config


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self):
        """
        Возвращает курсы в едином формате:
        {
          "BTC_USD": 59337.21,
          "ETH_USD": 3720.00,
          ...
        }
        """
        raise NotImplementedError


class CoinGeckoClient(BaseApiClient):
    def __init__(self):
        self.cfg = get_config()

    def fetch_rates(self):
        ids = []
        for code in self.cfg.CRYPTO_CURRENCIES:
            if code in self.cfg.CRYPTO_ID_MAP:
                ids.append(self.cfg.CRYPTO_ID_MAP[code])

        if not ids:
            return {}

        params = {
            "ids": ",".join(ids),
            "vs_currencies": self.cfg.BASE_FIAT_CURRENCY.lower(),
        }

        try:
            resp = requests.get(
                self.cfg.COINGECKO_URL,
                params=params,
                timeout=self.cfg.REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка сети при запросе CoinGecko: {e}")

        if resp.status_code != 200:
            raise ApiRequestError(f"CoinGecko вернул статус {resp.status_code}")

        try:
            data = resp.json()
        except Exception:
            raise ApiRequestError("CoinGecko вернул некорректный JSON")

        result = {}
        base = self.cfg.BASE_FIAT_CURRENCY.lower()

        for code, cg_id in self.cfg.CRYPTO_ID_MAP.items():
            if cg_id in data and isinstance(data[cg_id], dict) and base in data[cg_id]:
                result[f"{code}_{self.cfg.BASE_FIAT_CURRENCY}"] = float(data[cg_id][base])

        return result


class ExchangeRateApiClient(BaseApiClient):
    def __init__(self):
        self.cfg = get_config()
        if not self.cfg.EXCHANGERATE_API_KEY:
            raise ApiRequestError("Не задан EXCHANGERATE_API_KEY (проверьте .env)")

    def fetch_rates(self):
        # URL: https://v6.exchangerate-api.com/v6/<KEY>/latest/USD
        url = f"{self.cfg.EXCHANGERATE_API_URL}/{self.cfg.EXCHANGERATE_API_KEY}/latest/{self.cfg.BASE_FIAT_CURRENCY}"

        try:
            resp = requests.get(url, timeout=self.cfg.REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка сети при запросе ExchangeRate-API: {e}")

        if resp.status_code != 200:
            raise ApiRequestError(f"ExchangeRate-API вернул статус {resp.status_code}")

        try:
            data = resp.json()
        except Exception:
            raise ApiRequestError("ExchangeRate-API вернул некорректный JSON")

        rates = data.get("conversion_rates")
        if rates is None:
            rates = data.get("rates")

        if not isinstance(rates, dict):
            raise ApiRequestError("ExchangeRate-API: нет поля conversion_rates/rates в ответе")

        result = {}
        base = self.cfg.BASE_FIAT_CURRENCY

        for code in self.cfg.FIAT_CURRENCIES:
            if code in rates:
                v = float(rates[code])
                if v == 0:
                    continue
                result[f"{code}_{base}"] = 1.0 / v

        return result