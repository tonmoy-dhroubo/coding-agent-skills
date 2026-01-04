# Security Assessment: playwright-skill

## Executive Summary
- Overall Risk Level: USE WITH CAUTION
- Source: GitHub (https://github.com/lackeyjb/playwright-skill)
- Evaluation Date: 2026-01-04
- Evaluator: Claude AI (Agent Skill Evaluator Skill)
- Critical Findings: No prompt injection or exfiltration patterns detected; however, the skill executes arbitrary Playwright scripts and auto-installs dependencies via `npm install`/`npx`, which introduces supply-chain and execution risk.
- Recommendation: Use with caution; review any automation scripts before execution and run in a controlled environment.

## Source & Provenance
- Repository: `lackeyjb/playwright-skill` (public GitHub repo)
- Owner: `lackeyjb` (public GitHub user)
- Repo metadata (GitHub API): ~1105 stars, JavaScript, MIT license; indicates active usage and community interest.
- No obvious provenance red flags in repository metadata; no verified publisher information available.

## Skill Structure Overview
- File structure (skills/playwright-skill):
  - `SKILL.md` (primary instructions)
  - `run.js` (executor)
  - `lib/helpers.js` (automation helpers)
  - `package.json` (dependencies)
  - `API_REFERENCE.md` (documentation)
- No additional `assets/` or `references/` directories in the skill package itself.

## SKILL.md Analysis
### Prompt Injection Detection
- No system prompt override patterns (e.g., “ignore previous instructions”), role manipulation, encoded directives, or hidden instruction techniques detected.
- Examples in `SKILL.md` are plain Playwright usage snippets and do not contain obfuscated payloads.

### Suspicious Behavioral Instructions
- The skill instructs the agent to execute Node/Playwright scripts and to auto-detect local dev servers. This aligns with the stated purpose (browser automation).
- No instructions to hide actions, bypass user consent, or exfiltrate data.

### Over-Permissioned Requests
- The workflow expects executing arbitrary automation code and running `node`/`npm` commands. This is expected for a Playwright executor but is inherently powerful.
- No explicit request for credential scraping or access to sensitive local files in SKILL.md.

## Scripts Security Analysis
- `run.js`:
  - Uses `child_process.execSync` to run `npm install` and `npx playwright install chromium` if Playwright is missing. This is a legitimate setup step but introduces supply-chain risk by pulling packages from npm at runtime.
  - Executes user-provided code by writing it to a temporary `.temp-execution-*.js` file and `require()`-ing it. This is the expected executor behavior, but it means any script content is executed with local user permissions.
- `lib/helpers.js`:
  - Provides convenience helpers (click, type, screenshots, auth, server detection). No external network calls beyond localhost dev-server detection (HTTP HEAD to `localhost` ports).
  - No obfuscation, base64 decode/exec, or suspicious external URLs.

## References & Assets Analysis
- No `references/` or `assets/` directories present in the skill package.
- `API_REFERENCE.md` is documentation-only; no hidden instructions detected in quick scan.

## Community Feedback & External Research
- GitHub repository search confirms the repo exists and is the top match for “playwright-skill”.
- GitHub issue search for “security” in `lackeyjb/playwright-skill` returned no security reports (only a test suite PR appeared in the results).
- General web search via DuckDuckGo was blocked by bot challenge from this environment, so broader community feedback (Reddit/Twitter/forums) could not be verified.

## Attack Pattern Analysis
- No prompt injection patterns detected (no “ignore previous instructions,” hidden Unicode, conditional triggers, or data exfiltration instructions).
- No malicious code patterns detected (no obfuscated code, no external callbacks, no credential harvesting). The only system command execution is for dependency installation, which is a common and disclosed pattern.

## Risk Assessment

### Detailed Scoring
| Dimension | Score (0-100) | Justification |
|-----------|---------------|--------------|
| Prompt Injection | 90 | No override or hidden instruction patterns in `SKILL.md`. |
| Code Safety | 72 | Uses `execSync` to run `npm install` and `npx playwright install chromium`; legitimate but introduces supply-chain risk. |
| Data Privacy | 70 | Automation scripts can interact with sensitive sites and credentials; no exfiltration logic detected in skill code. |
| Source Trust | 75 | Public repo with significant stars and MIT license, but no independent security audits found. |
| Functionality | 85 | Behavior matches stated purpose; executor and helpers are straightforward. |
| **OVERALL RATING** | 78 | Generally safe for intended use, but execution and dependency installation require caution. |

### Threat Summary
- Supply-chain risk from auto-installing Playwright and dependencies at runtime.
- Arbitrary code execution risk if untrusted automation scripts are run.

### False Positive Analysis
- System command execution via `npm install`/`npx` is a common, legitimate setup step for Playwright. No evidence of misuse or hidden payloads.

## Final Verdict

**Recommendation**: USE WITH CAUTION

**Reasoning**: The skill is transparent and aligned with its purpose, but it executes arbitrary automation scripts and auto-installs dependencies, which adds supply-chain and execution risk.

**Specific Concerns**:
- Auto-install behavior (dependency downloads) may pull untrusted packages if the npm ecosystem is compromised.
- Any script executed via `run.js` runs with local user permissions.

**Safe Use Cases**:
- Controlled environments where scripts are authored or reviewed by the user.
- Local testing against known URLs, using least-privilege credentials.

**Alternative Skills**:
- None identified in this evaluation.

## Evaluation Limitations
- Unable to write the assessment file to `/mnt/user-data/outputs/` due to permission errors; report saved locally instead.
- General web search results (Reddit/Twitter/security forums) could not be accessed due to bot challenge restrictions.

## Evidence Appendix
- `run.js` uses `child_process.execSync('npm install')` and `execSync('npx playwright install chromium')` for setup.
- `run.js` writes temporary execution files `.temp-execution-*.js` and `require()`s them.
- `lib/helpers.js` dev server detection only targets `http://localhost:<port>` and does not call external domains.
