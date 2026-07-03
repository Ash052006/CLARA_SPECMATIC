# Testing Clara With Specmatic

Clara uses Specmatic for three contract-driven workflows:

- Provider contract testing against the live FastAPI app.
- Service virtualization through a Specmatic stub server.
- Backward compatibility checks for contract changes.

The executable contract lives at `contracts/clara_api.yaml`.

## Install Dependencies

```bash
pip install -r requirements.txt
npm install
```

## Run Smoke Tests

```bash
pytest
```

These tests are intentionally small. They check Clara's local FastAPI behavior but do not replace Specmatic contract testing.

## Run Specmatic Provider Contract Tests

On Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_specmatic_tests.ps1
```

Manually, in any shell:

```bash
CLARA_CONTRACT_TEST_MODE=1 uvicorn main:app --host 127.0.0.1 --port 8000
npx specmatic test contracts/clara_api.yaml --testBaseURL=http://127.0.0.1:8000
```

Specmatic calls Clara as a real provider and validates status codes, response bodies, and example compatibility.

## Run Service Virtualization

Start a simulated Clara API from the contract:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_specmatic_stub.ps1
```

Or directly:

```bash
npx specmatic stub contracts/clara_api.yaml --host=127.0.0.1 --port=9000
```

Consumers, UI prototypes, or AI coding agents can call `http://127.0.0.1:9000` without starting Clara or touching Google credentials, local models, ChromaDB, or tokens.

Example:

```bash
curl http://127.0.0.1:9000/
curl http://127.0.0.1:9000/health
curl "http://127.0.0.1:9000/chat/What%20time%20is%20my%20next%20meeting"
```

## Run Backward Compatibility Checks

Specmatic compares the current contract against the base branch and fails on incompatible changes:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_backward_compatibility_check.ps1
```

Direct command:

```bash
npx specmatic backward-compatibility-check --repo-dir=. --base-branch=origin/main --target-path=contracts/clara_api.yaml
```

A baseline copy is also kept at `contracts/history/clara_api_v1.yaml` for human review and release notes.

## CI/CD

`.github/workflows/test.yml` runs all three workflows:

1. Pytest smoke tests.
2. Specmatic backward compatibility check.
3. Specmatic provider contract tests against a live Clara instance.
4. Specmatic service virtualization smoke test.
