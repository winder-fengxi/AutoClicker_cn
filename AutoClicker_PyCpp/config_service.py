import json
import os
from typing import Any, Dict


def load_languages(base_dir: str) -> Dict[str, Dict[str, str]]:
    """加载语言配置文件。"""
    lang_path = os.path.join(base_dir, "languages.json")
    try:
        with open(lang_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {
            "en": {
                "title": "AutoClicker",
                "stopped": "Stopped",
                "running": "Running...",
                "error_title": "Error",
                "invalid_time_interval": "Invalid time interval! Please enter numbers only.",
                "settings_saved": "Settings Saved!",
            }
        }


def load_settings(base_dir: str) -> Dict[str, Any]:
    """加载 settings.json。"""
    settings_path = os.path.join(base_dir, "settings.json")
    if not os.path.exists(settings_path):
        return {}
    try:
        with open(settings_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_settings(base_dir: str, settings: Dict[str, Any]) -> None:
    """保存 settings.json。"""
    settings_path = os.path.join(base_dir, "settings.json")
    with open(settings_path, "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)
