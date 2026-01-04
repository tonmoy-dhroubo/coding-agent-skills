import re
import shutil
from typing import Dict


def parse_db_url(url: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    if url.startswith("jdbc:"):
        url = url[len("jdbc:") :]
    if url.startswith("postgres"):
        result["engine"] = "postgres"
    elif url.startswith("mysql"):
        result["engine"] = "mysql"
    elif url.startswith("sqlite"):
        result["engine"] = "sqlite"

    match = re.match(r"\w+://([^:/]+)(?::(\d+))?/([^?]+)", url)
    if match:
        result["host"] = match.group(1)
        if match.group(2):
            result["port"] = match.group(2)
        result["database"] = match.group(3)
    return result


def detect_db_engine(db_info: Dict[str, str]) -> str:
    engine = db_info.get("engine")
    if engine:
        return engine
    url = db_info.get("url", "")
    if "postgres" in url:
        return "postgres"
    if "mysql" in url:
        return "mysql"
    if "sqlite" in url:
        return "sqlite"
    return "unknown"


def detect_db_clis() -> Dict[str, str]:
    clis = {}
    for name in ["psql", "mysql", "sqlite3", "mongosh"]:
        path = shutil.which(name)
        if path:
            clis[name] = path
    return clis
