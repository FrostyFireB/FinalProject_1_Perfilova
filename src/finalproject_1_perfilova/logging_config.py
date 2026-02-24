import logging
from pathlib import Path


from finalproject_1_perfilova.infra.settings import SettingsLoader


def setup_logging():
    s = SettingsLoader()

    log_dir = Path(s.get("LOG_DIR", "logs"))
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(asctime)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )