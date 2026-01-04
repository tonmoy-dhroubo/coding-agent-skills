import os
from typing import Any, Dict, Optional

from .util import read_json, read_text

DEFAULT_CONFIG = {
    "allowDelete": False,
    "timeoutSeconds": 10,
    "retries": 1,
}


def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return dict(DEFAULT_CONFIG)
    if not os.path.exists(path):
        return dict(DEFAULT_CONFIG)
    data = None
    if path.endswith((".yml", ".yaml")):
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(read_text(path)) or {}
        except Exception:
            data = None
    else:
        data = read_json(path)
    if data is None:
        return dict(DEFAULT_CONFIG)
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


def resolve_config(project_root: str, config_path: Optional[str]) -> Dict[str, Any]:
    if config_path:
        return load_config(config_path)
    default_path = os.path.join(project_root, "skill.config.json")
    return load_config(default_path)
