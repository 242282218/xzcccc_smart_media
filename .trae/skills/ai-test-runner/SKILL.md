---
name: "ai-test-runner"
description: "Unified, non-interactive test execution via scripts/run_tests.py with logs/test outputs and dynamic timeouts. Use when running tests, analyzing failures, or enforcing container-only testing."
---

# AI Test Runner (smart_media)

Use the unified Python test runner to execute tests in a non-interactive, timeout-safe way and collect structured logs.

## When to Invoke

- You need to run tests locally (Dev Container) or in CI
- You need structured logs for analysis (`logs/test/`)
- You must enforce the no-interactive-shell testing policy

## Steps

1. Ensure config exists:
   - `ai/test_config.yaml`
2. Run the runner:
   ```powershell
   python scripts/run_tests.py --suite fast
   ```
3. Review logs:
   - `logs/test/summary.json`
   - `logs/test/stdout.log`
   - `logs/test/stderr.log`
   - `logs/test/junit.xml`

## Rules

- Do not run `pytest`, `npm test`, or other direct test commands
- Do not enter an interactive shell for testing
