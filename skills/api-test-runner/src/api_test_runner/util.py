import json
import os
import re
from typing import Dict, Iterable, List, Optional

SECRET_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "apikey",
    "api_key",
    "authorization",
}


def read_text(path: str, max_bytes: int = 512 * 1024) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read(max_bytes)
    except OSError:
        return ""


def read_json(path: str) -> Optional[Dict]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def find_files(root: str, names: Iterable[str]) -> List[str]:
    hits: List[str] = []
    names_set = set(names)
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {"node_modules", "target", "build", "dist", ".git"}]
        for filename in files:
            if filename in names_set:
                hits.append(os.path.join(base, filename))
    return hits


def find_files_by_ext(root: str, exts: Iterable[str]) -> List[str]:
    hits: List[str] = []
    exts_set = set(exts)
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {"node_modules", "target", "build", "dist", ".git"}]
        for filename in files:
            _, ext = os.path.splitext(filename)
            if ext in exts_set:
                hits.append(os.path.join(base, filename))
    return hits


def parse_env_text(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip().strip("'\"")
    return result


def redact_value(value: str) -> str:
    if not value:
        return value
    if len(value) <= 4:
        return "****"
    return value[:2] + "***" + value[-2:]


def redact_dict(data: Dict) -> Dict:
    redacted = {}
    for key, value in data.items():
        if isinstance(value, dict):
            redacted[key] = redact_dict(value)
        elif isinstance(value, list):
            redacted[key] = [redact_dict(v) if isinstance(v, dict) else v for v in value]
        else:
            if key.lower() in SECRET_KEYS:
                redacted[key] = redact_value(str(value))
            else:
                redacted[key] = value
    return redacted


def sanitize_text(text: str) -> str:
    def repl(match: re.Match) -> str:
        return match.group(1) + "***"

    patterns = [
        r"(password=)[^&\s]+",
        r"(token=)[^&\s]+",
        r"(authorization:)[^\n]+",
    ]
    for pattern in patterns:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text
