#!/usr/bin/env bash
set -euo pipefail

command=${1:-run}
shift || true

project_root=$(pwd)
config_path=""
base_url=""
discovery_only=false
generate_only=false
discover_cmd=false
run_cmd=false

while [ $# -gt 0 ]; do
  case "$1" in
    --project-root)
      project_root="$2"; shift 2 ;;
    --config)
      config_path="$2"; shift 2 ;;
    --base-url)
      base_url="$2"; shift 2 ;;
    --only-discovery)
      discovery_only=true; shift ;;
    --only-generate)
      generate_only=true; shift ;;
    --dry-run)
      generate_only=true; shift ;;
    --run)
      run_cmd=true; shift ;;
    *)
      shift ;;
  esac
done

node_cli="$(command -v node || true)"
python_cli="$(command -v python3 || true)"

if [ -n "$python_cli" ]; then
  PYTHONPATH=src python3 -m api_test_runner "$command" --project-root "$project_root" ${config_path:+--config "$config_path"} ${base_url:+--base-url "$base_url"}
  exit $?
fi

if [ -n "$node_cli" ]; then
  node src/node_cli.js "$command" --project-root "$project_root" ${config_path:+--config "$config_path"} ${base_url:+--base-url "$base_url"}
  exit $?
fi

echo "No python3 or node found; bash fallback requires jq and manual plan creation." >&2
exit 1
