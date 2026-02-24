import json
from pathlib import Path

from finalproject_1_perfilova.infra.settings import SettingsLoader


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = SettingsLoader()
        return cls._instance

    def _data_dir(self):
        data_dir = self._settings.get("DATA_DIR", "data")
        return Path.cwd() / data_dir

    def read(self, filename: str, default):
        path = self._data_dir() / filename
        if not path.exists():
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def write(self, filename: str, data):
        path = self._data_dir() / filename
        path.parent.mkdir(exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)