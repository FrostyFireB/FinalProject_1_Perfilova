from pathlib import Path
import tomllib


class SettingsLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
            cls._instance._settings = {}
        return cls._instance

    def load(self):
        # дефолт, если в pyproject.toml ничего не задано
        data_dir = str(Path.cwd() / "data")
        logs_dir = str(Path.cwd() / "logs")
        self._settings = {
            "DATA_DIR": data_dir,
            "RATES_TTL_SECONDS": 300,
            "BASE_CURRENCY": "USD",
            "LOG_DIR": logs_dir,
            "LOG_FILE": str(Path(logs_dir) / "app.log"),
        }

        pyproject_path = Path.cwd() / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, "rb") as f:
                    cfg = tomllib.load(f)

                tool_cfg = cfg.get("tool", {})
                valutatrade_cfg = tool_cfg.get("valutatrade", {})

                if "DATA_DIR" in valutatrade_cfg:
                    self._settings["DATA_DIR"] = str(valutatrade_cfg["DATA_DIR"])
                if "RATES_TTL_SECONDS" in valutatrade_cfg:
                    self._settings["RATES_TTL_SECONDS"] = int(valutatrade_cfg["RATES_TTL_SECONDS"])
                if "BASE_CURRENCY" in valutatrade_cfg:
                    self._settings["BASE_CURRENCY"] = str(valutatrade_cfg["BASE_CURRENCY"]).upper()
                if "LOG_DIR" in valutatrade_cfg:
                    self._settings["LOG_DIR"] = str(valutatrade_cfg["LOG_DIR"])
                    self._settings["LOG_FILE"] = str(Path(self._settings["LOG_DIR"]) / "app.log")

            except Exception:
                pass

        self._loaded = True

    def get(self, key: str, default=None):
        if not self._loaded:
            self.load()
        return self._settings.get(key, default)

    def reload(self):
        self.load()