import json
from pathlib import Path

CONFIG_PATH = CONFIG_PATH = Path(__file__).parent / "config.json"
_config = {}

def load():
    global _config
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open() as f:
            _config = json.load(f)
    else:
        _config = {}

def get(key, default=None):
    return _config.get(key, default)
