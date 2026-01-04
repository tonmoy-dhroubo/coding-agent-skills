import json
from typing import Dict, List


def format_markdown_report(results: List[Dict]) -> str:
    lines = ["# API Test Report", "", "| Method | Path | Status | Latency (ms) | Notes |", "| --- | --- | --- | --- | --- |"]
    for item in results:
        lines.append(
            "| {method} | {path} | {status} | {latency} | {notes} |".format(
                method=item.get("method", ""),
                path=item.get("path", ""),
                status=item.get("status", ""),
                latency=item.get("latency_ms", ""),
                notes=item.get("notes", ""),
            )
        )
    return "\n".join(lines) + "\n"


def format_json_report(results: List[Dict]) -> str:
    return json.dumps({"results": results}, indent=2)
