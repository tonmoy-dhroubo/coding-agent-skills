import argparse
import json
import os
from typing import Dict, List

from .config import resolve_config
from .discovery import detect_backend, detect_db_clis, detect_db_engine, discover_endpoints, discover_env
from .execution import run_runner
from .generation import detect_runtime, generate_runner
from .planning import infer_order
from .util import redact_dict


def build_plan(endpoints: List[Dict], config: Dict) -> List[Dict]:
    plan = []
    auth = config.get("auth") or {}
    for ep in endpoints:
        entry = dict(ep)
        method = entry.get("method", "GET")
        if method in {"POST", "PUT", "PATCH"}:
            if auth and entry.get("path") == auth.get("loginEndpoint"):
                payload = auth.get("payload")
                if payload is None:
                    user = auth.get("username")
                    password = auth.get("password")
                    payload = {"username": user, "password": password}
                entry["payload"] = payload
                entry["payload_guess"] = not bool(payload)
            else:
                entry["payload"] = config.get("defaultPayload", {})
                entry["payload_guess"] = True
        plan.append(entry)
    return plan


def detect_auth(endpoints: List[Dict], config: Dict) -> None:
    if config.get("auth"):
        return
    for ep in endpoints:
        path = ep.get("path", "")
        if "login" in path or "auth" in path or "token" in path:
            config["auth"] = {
                "type": "bearer",
                "loginEndpoint": path,
                "tokenPath": "token",
            }
            return


def gather_discovery(project_root: str, config: Dict) -> Dict:
    env_data = discover_env(project_root)
    backend = detect_backend(project_root)
    endpoints = discover_endpoints(project_root)
    db_info = env_data.get("db", {})
    db_engine = detect_db_engine(db_info)
    db_clis = detect_db_clis()

    base_url = config.get("baseUrl") or env_data.get("base_url") or "http://localhost:8080"

    return {
        "backend": backend,
        "env": env_data,
        "endpoints": endpoints,
        "db": db_info,
        "db_engine": db_engine,
        "db_clis": db_clis,
        "base_url": base_url,
    }


def print_discovery(summary: Dict) -> None:
    print("Backend:", ", ".join(summary.get("backend") or []) or "unknown")
    print("Base URL:", summary.get("base_url"))
    print("Endpoints:", len(summary.get("endpoints") or []))
    print("DB engine:", summary.get("db_engine"))
    print("DB CLIs:", ", ".join(summary.get("db_clis") or []) or "none")


def main() -> int:
    parser = argparse.ArgumentParser(prog="api-test-runner")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--project-root", default=os.getcwd())
        subparser.add_argument("--base-url", dest="base_url")
        subparser.add_argument("--config")
        subparser.add_argument("--dry-run", action="store_true")
        subparser.add_argument("--no-db", action="store_true")
        subparser.add_argument("--only-discovery", action="store_true")
        subparser.add_argument("--only-generate", action="store_true")
        subparser.add_argument("--run", action="store_true")
        subparser.add_argument("--report-path")

    add_common(sub.add_parser("discover"))
    add_common(sub.add_parser("generate"))
    add_common(sub.add_parser("run"))

    args = parser.parse_args()
    project_root = os.path.abspath(args.project_root)
    config = resolve_config(project_root, args.config)
    if args.base_url:
        config["baseUrl"] = args.base_url

    discovery = gather_discovery(project_root, config)
    print_discovery(discovery)

    endpoints = discovery.get("endpoints", [])
    detect_auth(endpoints, config)
    ordered = infer_order(endpoints, config)
    plan = build_plan(ordered, config)

    if args.only_discovery or args.command == "discover":
        print(json.dumps(redact_dict(discovery), indent=2))
        return 0

    runtime = detect_runtime()
    report_dir = os.path.join(project_root, "reports")
    artifacts_dir = os.path.join(project_root, "artifacts")
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(artifacts_dir, exist_ok=True)
    report_path = args.report_path or os.path.join(report_dir, "api-test-report.md")
    runner_path = os.path.join(project_root, ".api-test-runner", "generated_runner")
    if runtime == "python":
        runner_path += ".py"
    elif runtime == "node":
        runner_path += ".js"
    else:
        runner_path += ".sh"

    payload_config = dict(config)
    payload_config["baseUrl"] = discovery.get("base_url")
    payload_db = discovery.get("db") if not args.no_db else {}
    if payload_db:
        payload_db = dict(payload_db)
        payload_db["engine"] = discovery.get("db_engine")
    payload_config["db"] = payload_db
    payload_config["dbClis"] = discovery.get("db_clis") if not args.no_db else {}

    generate_runner(plan, payload_config, runtime, runner_path, report_path, artifacts_dir)
    print("Generated runner:", runner_path)

    if args.only_generate or args.command == "generate" or args.dry_run:
        print("Dry-run enabled; no network calls executed.")
        return 0

    if args.command == "run" or args.run:
        return run_runner(runtime, runner_path)

    return 0
