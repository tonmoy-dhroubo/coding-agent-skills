#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

function parseArgs() {
  const args = process.argv.slice(2);
  const options = { command: args[0] || "run" };
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith("--")) {
      const key = arg.replace(/^--/, "");
      const value = args[i + 1] && !args[i + 1].startsWith("--") ? args[++i] : true;
      options[key.replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = value;
    }
  }
  return options;
}

function loadConfig(projectRoot, configPath) {
  const target = configPath || path.join(projectRoot, "skill.config.json");
  if (!fs.existsSync(target)) return { retries: 1, timeoutSeconds: 10 };
  try {
    return Object.assign({ retries: 1, timeoutSeconds: 10 }, JSON.parse(fs.readFileSync(target, "utf-8")));
  } catch (err) {
    return { retries: 1, timeoutSeconds: 10 };
  }
}

function discoverEndpoints(projectRoot) {
  const candidates = ["openapi.json", "swagger.json"];
  for (const name of candidates) {
    const file = path.join(projectRoot, name);
    if (!fs.existsSync(file)) continue;
    try {
      const data = JSON.parse(fs.readFileSync(file, "utf-8"));
      const endpoints = [];
      const paths = data.paths || {};
      Object.keys(paths).forEach((p) => {
        Object.keys(paths[p] || {}).forEach((method) => {
          endpoints.push({ method: method.toUpperCase(), path: p, source: "openapi" });
        });
      });
      return endpoints;
    } catch (_) {}
  }
  return [];
}

function inferOrder(endpoints, config) {
  const allowDelete = Boolean(config.allowDelete);
  return endpoints.filter((ep) => !(ep.method === "DELETE" && !allowDelete));
}

function buildPlan(endpoints) {
  return endpoints.map((ep) => {
    const entry = Object.assign({}, ep);
    if (["POST", "PUT", "PATCH"].includes(entry.method)) {
      entry.payload = {};
      entry.payload_guess = true;
    }
    return entry;
  });
}

function generateRunner(plan, config, projectRoot, reportPath) {
  const templatePath = path.join(__dirname, "..", "templates", "runner_js.tmpl");
  const template = fs.readFileSync(templatePath, "utf-8");
  const payload = {
    plan,
    config,
    report_path: reportPath,
    artifacts_dir: path.join(projectRoot, "artifacts"),
  };
  const rendered = template.replace("{{PAYLOAD_JSON}}", JSON.stringify(payload, null, 2));
  const outDir = path.join(projectRoot, ".api-test-runner");
  fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, "generated_runner.js");
  fs.writeFileSync(outPath, rendered);
  return outPath;
}

function main() {
  const options = parseArgs();
  const projectRoot = path.resolve(options.projectRoot || process.cwd());
  const config = loadConfig(projectRoot, options.config);
  if (options.baseUrl) config.baseUrl = options.baseUrl;

  const endpoints = discoverEndpoints(projectRoot);
  console.log(`Endpoints: ${endpoints.length}`);

  if (options.onlyDiscovery || options.command === "discover") {
    console.log(JSON.stringify({ endpoints }, null, 2));
    return;
  }

  const ordered = inferOrder(endpoints, config);
  const plan = buildPlan(ordered);
  const reportPath = options.reportPath || path.join(projectRoot, "reports", "api-test-report.md");
  const runnerPath = generateRunner(plan, config, projectRoot, reportPath);
  console.log(`Generated runner: ${runnerPath}`);

  if (options.onlyGenerate || options.command === "generate" || options.dryRun) {
    console.log("Dry-run enabled; no network calls executed.");
    return;
  }

  const { spawnSync } = require("child_process");
  spawnSync("node", [runnerPath], { stdio: "inherit" });
}

main();
