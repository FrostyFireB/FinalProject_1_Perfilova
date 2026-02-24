import json
from pathlib import Path


def data_dir():
    cwd = Path.cwd()
    if (cwd / "data").exists():
        return cwd / "data"
    
    for parent in cwd.parents:
        if (parent / "data").exists():
            return parent / "data"

    return Path(__file__).resolve().parents[3] / "data"


def read_json(filename, default):
    path = data_dir() / filename
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filename, data):
    path = data_dir() / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)