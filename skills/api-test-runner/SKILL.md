---
name: api-test-runner
description: Discover backend API endpoints, infer safe call order, generate a runnable API test runner script, and produce Markdown/JSON reports. Use when you need to scan a backend project for configs, extract base URL and DB info, auto-generate API test calls with retries/auth, optionally seed/inspect the DB with local DB CLIs, or run a dry-run discovery/generation workflow.
---

# API Test Runner Skill

Build a reusable test runner for arbitrary backend projects. Detect configuration, infer endpoints and call order, generate a script, and optionally execute it to produce reports and artifacts.

## Prerequisites

- Prefer Python 3 for discovery and generation.
- Fall back to Node.js if Python is unavailable.
- Fall back to Bash if neither Python nor Node is available.
- Avoid network calls in dry-run mode.

## Quick Start

- Run discovery only:
  - `PYTHONPATH=src python -m api_test_runner discover --project-root /path/to/project`
- Generate only:
  - `PYTHONPATH=src python -m api_test_runner generate --project-root /path/to/project`
- Full run (generate + execute):
  - `PYTHONPATH=src python -m api_test_runner run --project-root /path/to/project`
- Dry-run (generate only, no network calls):
  - `PYTHONPATH=src python -m api_test_runner run --project-root /path/to/project --dry-run`

If Python is unavailable, use the Node fallback with reduced features:
- `node src/node_cli.js run --project-root /path/to/project`
  - Node fallback only reads JSON OpenAPI specs and does not perform DB seeding/inspection.

## Detection Workflow

Follow this order:

1) Detect backend type (Spring/Nest/Express/etc) using file heuristics.
2) Locate config files (`.env*`, `application.yml`, `application.properties`, `docker-compose.yml`).
3) Extract base URL and DB config (host, port, DB name, user).
4) Detect DB engine and available DB CLI tools (psql/mysql/sqlite3/mongosh).
5) Discover endpoints via:
   - OpenAPI/Swagger spec if found
   - Source scan heuristics
   - Route listing files if found
6) Infer how to start the backend locally:
   - Prefer existing scripts (`package.json` scripts, `Makefile`, `docker-compose.yml`, `Dockerfile`)
   - Record a start command + expected port/health endpoint
7) Start the backend in the background before any API calls:
   - Use the inferred start command
   - Wait for health/ready endpoint or port open with a timeout
   - Capture PID/logs and stop the process on completion or failure
8) Infer a safe call order:
   - Health endpoints first
   - Auth/login next if detected
   - Create -> Read -> Update -> Delete (Delete disabled unless enabled)
9) Generate a test runner script (Python/Node/Bash based on runtime availability).
10) Optionally execute and write reports/artifacts.

## Configuration

Create `skill.config.json` (or `.yaml`) in the project root or pass `--config`.

Supported keys (all optional):

- `baseUrl`
- `auth`:
  - `type` (`bearer`)
  - `loginEndpoint`
  - `username` / `password` or `payload`
  - `tokenPath` (default: `token`)
- `seedSql` or `seedFile`
- `inspectDb` (default: false)
- `headers` (extra headers)
- `include` / `exclude` (endpoint path filters)
- `orderHints` (manual ordering hints)
- `allowDelete` (default: false)
- `timeoutSeconds` (default: 10)
- `retries` (default: 1)

## Safety Rules

- Never call DELETE unless `allowDelete` is true.
- Keep POST/PUT payloads minimal and safe; mark guessed payloads.
- Avoid brute-force auth; only attempt auth when patterns exist or config provides credentials.
- Redact secrets in logs and reports.
- Dry-run mode must not make network calls.

## Outputs

- `reports/api-test-report.md`
- `reports/api-test-report.json`
- `artifacts/` request/response dumps

## Troubleshooting

- If no endpoints are found, add `skill.config.json` with explicit `include` or `baseUrl`.
- If no DB CLI is found, DB seeding/introspection is skipped with a warning.
- If OpenAPI YAML parsing fails, install PyYAML or use JSON spec.
- If base URL detection is wrong, set `baseUrl` in config or pass `--base-url`.

## Agent Instructions

- Use discovery first; only run tests when explicitly asked or when safe.
- Prefer dry-run for safety and to show the generated script.
- Ask for credentials if auth endpoints are detected but no credentials are provided.
- Ask before enabling DELETE endpoints.
- If DB seeding is requested but DB CLI is missing, ask the user to install the CLI or provide a seed file.
- If running tests, try to start the backend in the background first; only skip if a running base URL is already confirmed or the user says it's handled.

## Examples

- Example config: `examples/sample-config.json`
- Example report: `examples/sample-report.md`
- Example JSON report: `examples/sample-report.json`
- Example fake project: `examples/demo_project/`
