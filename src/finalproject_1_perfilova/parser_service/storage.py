from datetime import datetime
from pathlib import Path

from finalproject_1_perfilova.infra.database import DatabaseManager


class RatesStorage:
    """
    Хранятся:
    - history: data/exchange_rates.json (исттория записей)
    - snapshot: data/rates.json (последние курсы для Core)
    """

    def __init__(self, rates_path: str, history_path: str):
        self.rates_path = rates_path
        self.history_path = history_path
        self.db = DatabaseManager()

    def append_history(self, records: list[dict]):
        history = self.db.read(self.history_path, [])
        history.extend(records)
        self.db.write(self.history_path, history)

    def write_snapshot(self, pairs: dict, last_refresh: str):
        obj = {
            "pairs": pairs,
            "last_refresh": last_refresh,
        }
        self.db.write(self.rates_path, obj)

    @staticmethod
    def make_id(pair: str, ts: str):
        return f"{pair}_{ts}"