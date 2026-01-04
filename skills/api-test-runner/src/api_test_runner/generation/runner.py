import json
import os
import shutil
from typing import Dict, List, Tuple

TEMPLATE_MAP = {
    "python": "runner_py.tmpl",
    "node": "runner_js.tmpl",
    "bash": "runner_sh.tmpl",
}


def detect_runtime() -> str:
    if shutil.which("python3"):
        return "python"
    if shutil.which("node"):
        return "node"
    return "bash"


def generate_runner(plan: List[Dict], config: Dict, runtime: str, output_path: str, report_path: str, artifacts_dir: str) -> str:
    template_name = TEMPLATE_MAP.get(runtime, TEMPLATE_MAP["python"])
    template_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "templates", template_name)
    template_path = os.path.abspath(template_path)
    with open(template_path, "r", encoding="utf-8") as handle:
        template = handle.read()

    payload = {
        "plan": plan,
        "config": config,
        "report_path": report_path,
        "artifacts_dir": artifacts_dir,
    }
    rendered = template.replace("{{PAYLOAD_JSON}}", json.dumps(payload, indent=2))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(rendered)
    return output_path
