import os
import re
from typing import Dict, List

from ..util import find_files, find_files_by_ext, read_json, read_text

OPENAPI_FILES = [
    "openapi.json",
    "openapi.yaml",
    "openapi.yml",
    "swagger.json",
    "swagger.yaml",
    "swagger.yml",
]


def discover_endpoints(project_root: str) -> List[Dict]:
    endpoints: List[Dict] = []
    endpoints.extend(from_openapi(project_root))
    endpoints.extend(from_source(project_root))
    deduped = {}
    for ep in endpoints:
        key = (ep.get("method"), ep.get("path"))
        deduped[key] = ep
    return list(deduped.values())


def from_openapi(project_root: str) -> List[Dict]:
    endpoints: List[Dict] = []
    for path in find_files(project_root, OPENAPI_FILES):
        if path.endswith(".json"):
            data = read_json(path) or {}
            endpoints.extend(_extract_openapi_paths(data))
        else:
            text = read_text(path)
            endpoints.extend(_extract_openapi_yaml(text))
    return endpoints


def _extract_openapi_paths(data: Dict) -> List[Dict]:
    endpoints: List[Dict] = []
    paths = data.get("paths") or {}
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method in methods.keys():
            endpoints.append({"method": method.upper(), "path": path, "source": "openapi"})
    return endpoints


def _extract_openapi_yaml(text: str) -> List[Dict]:
    endpoints: List[Dict] = []
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        return _extract_openapi_paths(data)
    except Exception:
        pass

    current_path = None
    for line in text.splitlines():
        if re.match(r"^\s*/", line):
            current_path = line.split(":", 1)[0].strip()
        elif current_path and re.match(r"^\s*(get|post|put|patch|delete):", line, re.I):
            method = line.split(":", 1)[0].strip().upper()
            endpoints.append({"method": method, "path": current_path, "source": "openapi-yaml"})
    return endpoints


def from_source(project_root: str) -> List[Dict]:
    endpoints: List[Dict] = []
    files = find_files_by_ext(project_root, {".java", ".kt", ".js", ".ts"})
    for path in files:
        text = read_text(path)
        if not text:
            continue
        endpoints.extend(_extract_spring(text))
        endpoints.extend(_extract_nest(text))
        endpoints.extend(_extract_express(text))
    return endpoints


def _extract_spring(text: str) -> List[Dict]:
    endpoints: List[Dict] = []
    mapping_patterns = {
        "GET": r"@GetMapping\(\"([^\"]*)\"\)",
        "POST": r"@PostMapping\(\"([^\"]*)\"\)",
        "PUT": r"@PutMapping\(\"([^\"]*)\"\)",
        "PATCH": r"@PatchMapping\(\"([^\"]*)\"\)",
        "DELETE": r"@DeleteMapping\(\"([^\"]*)\"\)",
    }
    for method, pattern in mapping_patterns.items():
        for match in re.findall(pattern, text):
            endpoints.append({"method": method, "path": _normalize_path(match), "source": "spring"})
    for match in re.findall(r"@RequestMapping\(\"([^\"]*)\"\)", text):
        endpoints.append({"method": "GET", "path": _normalize_path(match), "source": "spring"})
    return endpoints


def _extract_nest(text: str) -> List[Dict]:
    endpoints: List[Dict] = []
    controller_match = re.findall(r"@Controller\(['\"]([^'\"]*)['\"]\)", text)
    base = controller_match[0] if controller_match else ""
    mapping_patterns = {
        "GET": r"@Get\(['\"]?([^'\"]*)['\"]?\)",
        "POST": r"@Post\(['\"]?([^'\"]*)['\"]?\)",
        "PUT": r"@Put\(['\"]?([^'\"]*)['\"]?\)",
        "PATCH": r"@Patch\(['\"]?([^'\"]*)['\"]?\)",
        "DELETE": r"@Delete\(['\"]?([^'\"]*)['\"]?\)",
    }
    for method, pattern in mapping_patterns.items():
        for match in re.findall(pattern, text):
            path = "/".join([p for p in [base, match] if p])
            endpoints.append({"method": method, "path": _normalize_path(path), "source": "nestjs"})
    return endpoints


def _extract_express(text: str) -> List[Dict]:
    endpoints: List[Dict] = []
    for match in re.findall(r"(?:app|router)\.(get|post|put|patch|delete)\(\s*['\"]([^'\"]+)['\"]", text):
        method, path = match
        endpoints.append({"method": method.upper(), "path": _normalize_path(path), "source": "express"})
    return endpoints


def _normalize_path(path: str) -> str:
    if not path.startswith("/"):
        return "/" + path
    return path
