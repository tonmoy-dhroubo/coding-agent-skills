import re
from typing import Dict, List

METHOD_ORDER = {"POST": 1, "GET": 2, "PUT": 3, "PATCH": 4, "DELETE": 5}


def infer_order(endpoints: List[Dict], config: Dict) -> List[Dict]:
    include = config.get("include") or []
    exclude = config.get("exclude") or []
    allow_delete = config.get("allowDelete", False)

    filtered = []
    for ep in endpoints:
        path = ep.get("path") or ""
        if include and not any(token in path for token in include):
            continue
        if exclude and any(token in path for token in exclude):
            continue
        if ep.get("method") == "DELETE" and not allow_delete:
            continue
        filtered.append(ep)

    def score(ep: Dict) -> tuple:
        path = ep.get("path", "")
        method = ep.get("method", "GET")
        is_health = bool(re.search(r"health|status|ping", path, re.I))
        is_auth = bool(re.search(r"login|auth|token", path, re.I))
        base = path.strip("/").split("/")[0] if path.strip("/") else ""
        crud_order = METHOD_ORDER.get(method, 99)
        return (
            0 if is_health else 1,
            0 if is_auth else 1,
            base,
            crud_order,
            path,
        )

    ordered = sorted(filtered, key=score)
    return ordered
