import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "VisualDecoder"
PROFILES_DIR = CONFIG_DIR / "profiles"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "last_profile": "",
    "window_geometry": None,
    "riscv_opcodes_path": "./riscv-opcodes",
    "theme": "night",
}


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)


def load_global_config() -> dict:
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            save_global_config(DEFAULT_CONFIG)
            return dict(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save_global_config(config: dict) -> None:
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_config_value(key: str, default=None):
    cfg = load_global_config()
    return cfg.get(key, default)


def set_config_value(key: str, value) -> None:
    cfg = load_global_config()
    cfg[key] = value
    save_global_config(cfg)
