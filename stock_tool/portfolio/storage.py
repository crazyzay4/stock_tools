import json
from pathlib import Path

FILE = Path("portfolio.json")


def load_portfolio():
    if FILE.exists():
        return json.loads(FILE.read_text())
    return {}


def save_portfolio(data):
    FILE.write_text(json.dumps(data, indent=2))
