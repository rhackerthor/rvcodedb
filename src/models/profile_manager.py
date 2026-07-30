import json
import os
from pathlib import Path

from src.models.profile import Profile
from src.utils.config import PROFILES_DIR, ensure_config_dir


def list_profile_names() -> list[str]:
    ensure_config_dir()
    names = []
    for f in PROFILES_DIR.glob("*.json"):
        names.append(f.stem)
    return sorted(names)


def load_profile(name: str) -> Profile | None:
    ensure_config_dir()
    path = PROFILES_DIR / f"{name}.json"
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Profile.from_dict(data)
    except (json.JSONDecodeError, OSError, KeyError):
        return None


def save_profile(profile: Profile) -> None:
    ensure_config_dir()
    path = PROFILES_DIR / f"{profile.name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)


def delete_profile(name: str) -> bool:
    path = PROFILES_DIR / f"{name}.json"
    if path.exists():
        os.remove(path)
        return True
    return False


def rename_profile(old_name: str, new_name: str) -> bool:
    old_path = PROFILES_DIR / f"{old_name}.json"
    new_path = PROFILES_DIR / f"{new_name}.json"
    if not old_path.exists():
        return False
    if new_path.exists() and old_name != new_name:
        return False
    try:
        old_path.rename(new_path)
        return True
    except OSError:
        return False


def copy_profile(source_name: str, new_name: str) -> Profile | None:
    profile = load_profile(source_name)
    if profile is None:
        return None
    profile.name = new_name
    save_profile(profile)
    return profile
