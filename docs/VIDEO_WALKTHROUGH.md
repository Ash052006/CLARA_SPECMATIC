# Clara Specmatic Walkthrough Script

This document explains how Clara's Specmatic integration works, how to use it, and how to demonstrate it in a video walkthrough.

## 1. What Was Added

Clara is a FastAPI conversational AI project. It now uses Specmatic for three contract-driven workflows:

1. Contract testing
2. Service virtualization
3. Backward compatibility checking

The main contract file is:

```text
contracts/clara_api.yaml
```

That file is the API agreement. It describes Clara's endpoints, inputs, response bodies, error formats, and executable examples.

Specmatic reads this contract and can do three useful things:

```text
Specmatic test   -> checks the real Clara API
Specmatic stub   -> creates a fake Clara API from the contract
Specmatic compatibility check -> checks if contract changes break users
```

## 2. Important Files

```text
contracts/clara_api.yaml
```

This is the executable OpenAPI contract. It defines Clara's API boundary.

```text
specmatic.yaml
```

This tells Specmatic where the contract lives.

```text
scripts/run_specmatic_tests.ps1
```

Starts Clara in contract-test mode and runs Specmatic provider tests against the live API.

```text
scripts/run_specmatic_stub.ps1
```

Starts a virtual Clara API using the contract only.

```text
scripts/run_backward_compatibility_check.ps1
```

Runs Specmatic's backward compatibility check against the base branch.

```text
contracts/history/clara_api_v1.yaml
```

A saved baseline copy of the v1 contract for human review.

```text
main.py
```

Contains the FastAPI app and a contract-test mode so Specmatic can test Clara without loading Google services, model downloads, or real credentials.

## 3. Endpoints Covered By The Contract

The Specmatic contract covers these Clara endpoints:

```text
GET /
GET /health
GET /api/status
GET /chat/{message}
```

The `/chat/{message}` endpoint includes examples for:

```text
200 success response
400 empty-message error
500 internal-server-error response
```

## 4. How Contract-Test Mode Works

Normally Clara uses the real conversation stack:

```text
ConversationManager
Google Calendar / Gmail integrations
LLM and NLP logic
Memory and tools
```

For contract testing, we do not want tests to depend on secrets, Google tokens, model downloads, or slow external services.

So `main.py` supports this environment variable:

```powershell
CLARA_CONTRACT_TEST_MODE=1
```

When this is set, Clara uses a small deterministic test conversation manager. The HTTP API remains real, but the AI internals are replaced with predictable responses.

This gives stable Specmatic tests.

## 5. Install Requirements

Run these from the project root:

```powershell
cd "D:\Projects\CLARA - Copy"
```

Install Python dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install Specmatic through npm:

```powershell
npm install
```

## 6. Run The Smoke Tests

These are simple FastAPI checks. They are not the main contract tests, but they confirm the app can be imported and basic behavior works.

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Expected result:

```text
5 passed
```

## 7. Run Specmatic Contract Tests

This is the most important command for provider contract testing:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_specmatic_tests.ps1
```

What this script does:

1. Sets `CLARA_CONTRACT_TEST_MODE=1`
2. Starts Clara on `http://127.0.0.1:8000`
3. Waits until `/health` responds
4. Runs this Specmatic command:

```powershell
npx specmatic test contracts/clara_api.yaml --testBaseURL=http://127.0.0.1:8000
```

5. Stops Clara after the test run

Expected result:

```text
Tests run: 6
Successes: 6
Failures: 0
100% API Coverage
```

This proves that the live Clara API follows the contract.

## 8. Run Service Virtualization

Service virtualization means Specmatic pretends to be Clara.

Start the virtual Clara API:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_specmatic_stub.ps1
```

This starts a fake Clara service at:

```text
http://127.0.0.1:9000
```

Now test it from another terminal:

```powershell
curl http://127.0.0.1:9000/
```

```powershell
curl http://127.0.0.1:9000/health
```

```powershell
curl "http://127.0.0.1:9000/chat/What%20time%20is%20my%20next%20meeting"
```

This is useful because a frontend, integration, or AI coding agent can work with Clara's API before the real backend is running.

## 9. Run Backward Compatibility Check

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_backward_compatibility_check.ps1
```

This script runs:

```powershell
npx specmatic backward-compatibility-check --repo-dir=. --base-branch=origin/main --target-path=contracts/clara_api.yaml
```

What this means:

- Specmatic compares the current contract with the contract on `origin/main`.
- If an endpoint is removed, a field is removed, a type changes, or a response status changes, it can detect a breaking change.
- This helps Clara avoid accidentally breaking clients.

If no contract changes are detected, Specmatic may print:

```text
No specs were changed, skipping the check.
```

That is okay. It means there was nothing new to compare.

## 10. Package Commands

You can also run the workflows through npm:

```powershell
npm run test:contract
npm run stub
npm run virtualize
npm run compatibility
```

These commands are defined in:

```text
package.json
```

## 11. CI Workflow

The GitHub Actions workflow is here:

```text
.github/workflows/test.yml
```

It runs:

1. Python dependency installation
2. Specmatic installation
3. Pytest smoke tests
4. Specmatic backward compatibility check
5. Clara provider startup
6. Specmatic provider contract tests
7. Specmatic stub startup smoke test

This means pull requests can automatically prove that Clara's API contract still works.

## 12. 12-Minute Video Walkthrough Script

Use this section as the speaking script for your video. It is designed to fit a short walkthrough and includes the project explanation, code highlights, commands, issues, and the requested answer about Specmatic and AI-assisted development.

### 0:00-0:30 — Opening and problem statement

Say:

"In this walkthrough, I will show how I integrated Specmatic into Clara, my FastAPI conversational AI project. The goal is to make the API more reliable by turning the contract into something executable. I use Specmatic for contract testing, service virtualization, backward compatibility, and resilience-style checks."

### 0:30-1:30 — What Clara is and why this matters

Say:

"Clara is a conversational AI project with FastAPI endpoints. The API boundary matters because it is shared by humans, the frontend, integrations, and AI coding agents. If the contract is not explicit, small changes create integration surprises and downstream debugging effort."

### 1:30-3:00 — Explain Spec-Driven Development and executable contracts

Say:

"Spec-Driven Development means the API contract is treated as the source of truth before implementation. With Specmatic, that contract becomes executable. Instead of only documenting the API in prose, I can test it, stub it, and validate it automatically. This improves AI-assisted software development because the AI and the human both work against a precise, machine-checkable boundary."

### 3:00-4:30 — Show the project files

Show:

- `main.py`
- `contracts/clara_api.yaml`
- `specmatic.yaml`
- `scripts/run_specmatic_tests.ps1`
- `scripts/run_specmatic_stub.ps1`
- `scripts/run_backward_compatibility_check.ps1`

Say:

"The contract file is the core of the setup. It defines Clara's endpoints, expected schemas, and example responses. The implementation stays in FastAPI, and Specmatic uses the contract to verify that the app still behaves correctly."

### 4:30-6:00 — Explain contract-test mode

Say:

"Clara normally depends on AI services, memory, Gmail, and Google Calendar. Those are not ideal for contract tests because they can be slow, flaky, or require secrets. So I added a contract-test mode using `CLARA_CONTRACT_TEST_MODE=1`. In that mode, Clara still runs as a real FastAPI app, but the chat path uses a deterministic stub so the contract tests stay stable."

### 6:00-7:30 — Run smoke tests

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Say:

"These smoke tests confirm the FastAPI app loads and the core endpoints behave correctly."

### 7:30-9:00 — Run Specmatic contract tests

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_specmatic_tests.ps1
```

Say:

"This script starts Clara locally, waits for the health endpoint, and then runs Specmatic against the live API. If the implementation drifts from the contract, the test fails immediately."

### 9:00-10:15 — Run the stub and show virtualization

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_specmatic_stub.ps1
```

In another terminal, run:

```powershell
curl http://127.0.0.1:9000/
```

Say:

"This response comes from the Specmatic stub, not the real backend. That is powerful because frontends, integrations, and AI coding agents can work against the contract boundary without depending on the full AI implementation."

### 10:15-11:15 — Show backward compatibility and resilience checks

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_backward_compatibility_check.ps1
```

Then run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_resilience_tests.ps1
```

Say:

"These checks make it less likely that a change breaks existing consumers or surprises downstream systems. They also make the boundary easier to reason about when multiple agents or services are involved."

### 11:15-12:00 — Closing answer to the key questions

Say:

"Spec-Driven Development and executable contracts improve AI-assisted software development by giving both humans and AI a precise, machine-checkable contract to work from. They reduce uncertainty because the expected behavior is explicit, they reveal integration surprises early, and they cut downstream debugging effort because failures point to contract mismatches instead of vague assumptions. My goal was to use executable contracts to improve reliability, reduce integration uncertainty, and create clearer boundaries for humans and AI coding agents."

### Closing line

Say:

"Clara now has a contract-backed development workflow: tests for the real API, a stub for consumers, compatibility checks for change safety, and resilience-style validation for the contract boundary."

## 13. Resilience Testing With Specmatic

A useful extension to the contract workflow is resilience testing. The idea is to push the API contract harder by exercising the boundary with both valid and contract-invalid requests and observing whether the API responds safely and predictably.

This repository includes a lightweight resilience runner in:

```text
scripts/run_resilience_tests.ps1
```

Run it with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_resilience_tests.ps1
```

Or via Make:

```powershell
make resilience
```

This follows the spirit of the Specmatic Labs schema resiliency example: start the app, run the contract tests against the live API, and verify that the boundary behaves correctly under stress and contract-invalid input.

## 14. Quick Command Summary

```powershell
cd "D:\Projects\CLARA - Copy"
```

```powershell
.\.venv\Scripts\python.exe -m pytest
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_specmatic_tests.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_specmatic_stub.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_backward_compatibility_check.ps1
```
