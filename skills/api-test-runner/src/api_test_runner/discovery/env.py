import os
import re
from typing import Dict, List, Optional

from ..util import find_files, parse_env_text, read_text
from .db import parse_db_url


ENV_FILENAMES = [
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    "application.yml",
    "application.yaml",
    "application.properties",
    "docker-compose.yml",
    "compose.yaml",
]


def discover_env(project_root: str) -> Dict:
    env_files = find_files(project_root, ENV_FILENAMES)
    env_vars: Dict[str, str] = {}
    base_url = None
    db = {}

    for path in env_files:
        content = read_text(path)
        if path.endswith((".env", ".env.local", ".env.development", ".env.production")):
            env_vars.update(parse_env_text(content))
        elif path.endswith(".properties"):
            env_vars.update(parse_properties(content))
        elif path.endswith((".yml", ".yaml")):
            env_vars.update(parse_yaml(content))
        elif path.endswith(("docker-compose.yml", "compose.yaml")):
            env_vars.update(parse_compose(content))

    base_url = extract_base_url(env_vars)
    db = extract_db_info(env_vars)

    return {
        "env_files": env_files,
        "env_vars": env_vars,
        "base_url": base_url,
        "db": db,
    }


def parse_properties(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def parse_yaml(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and value and " " not in key:
            result[key] = value
    return result


def parse_compose(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    port_match = re.search(r"-\s*(\d+):\d+", text)
    if port_match:
        result["PORT"] = port_match.group(1)
    return result


def extract_base_url(env_vars: Dict[str, str]) -> Optional[str]:
    host = env_vars.get("HOST") or env_vars.get("SERVER_HOST") or "localhost"
    port = env_vars.get("PORT") or env_vars.get("SERVER_PORT") or env_vars.get("SERVER__PORT")
    if port:
        return f"http://{host}:{port}"
    return None


def extract_db_info(env_vars: Dict[str, str]) -> Dict:
    db = {}
    url = env_vars.get("DATABASE_URL") or env_vars.get("SPRING_DATASOURCE_URL")
    if url:
        db.update(parse_db_url(url))

    db_host = env_vars.get("DB_HOST") or env_vars.get("DATABASE_HOST")
    db_port = env_vars.get("DB_PORT")
    db_name = env_vars.get("DB_NAME") or env_vars.get("DATABASE_NAME")
    db_user = env_vars.get("DB_USER") or env_vars.get("DATABASE_USER")
    db_pass = env_vars.get("DB_PASSWORD") or env_vars.get("DATABASE_PASSWORD")
    if db_host:
        db["host"] = db_host
    if db_port:
        db["port"] = db_port
    if db_name:
        db["database"] = db_name
    if db_user:
        db["user"] = db_user
    if db_pass:
        db["password"] = db_pass
    return db
