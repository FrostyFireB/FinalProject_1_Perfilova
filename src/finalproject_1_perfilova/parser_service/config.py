import os
from dataclasses import dataclass
from pathlib import Path


def load_env():
    """
    Простой загрузчик .env
    ищет .env в текущей папке запуска и выше (до корня),
    кладёт значения в os.environ, если переменная ещё не задана.
    """
    env_file = None
    cur = Path.cwd()

    for p in [cur, *cur.parents]:
        candidate = p / ".env"
        if candidate.exists():
            env_file = candidate
            break

    if env_file is None:
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


@dataclass
class ParserConfig:
    EXCHANGERATE_API_KEY: str | None = None

    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    BASE_FIAT_CURRENCY: str = "USD"
    FIAT_CURRENCIES: tuple[str, ...] = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: tuple[str, ...] = ("BTC", "ETH", "SOL")
    CRYPTO_ID_MAP: dict[str, str] = None

    RATES_FILE_PATH: str = "rates.json"
    HISTORY_FILE_PATH: str = "exchange_rates.json"

    REQUEST_TIMEOUT: int = 10

    def __post_init__(self):
        if self.CRYPTO_ID_MAP is None:
            self.CRYPTO_ID_MAP = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
            }


def get_config():
    load_env()
    cfg = ParserConfig()
    cfg.EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")
    return cfg
