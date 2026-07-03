# Clara Specmatic Integration - 12 Minute Video Walkthrough Script

## 0:00 - 0:45 | Introduction

Hi everyone. In this video, I’ll walk through how I integrated Specmatic into my FastAPI project called Clara.

Clara is a conversational AI assistant with endpoints for health checks and chat processing. It also connects to things like Gmail, Google Calendar, memory, and AI processing.

The goal of this work was to make Clara’s API more reliable using executable contracts.

I implemented three Specmatic workflows:

```text
1. Contract testing
2. Service virtualization
3. Backward compatibility checking
```

By the end of this walkthrough, I’ll show how the contract is written, how the real API is tested, how a fake API can be generated from the contract, and how compatibility checks help prevent breaking changes.

## 0:45 - 1:45 | Project Overview

First, I’m in the Clara project folder.

The most important file for this integration is:

```text
contracts/clara_api.yaml
```

This is the OpenAPI contract for Clara.

In a normal project, an OpenAPI file can just be documentation. But with Specmatic, this file becomes executable.

That means Specmatic can read the contract and use it to test the real API, create a virtual API, and check whether future changes are backward compatible.

So this file becomes the source of truth for Clara’s API boundary.

The other important files are:

```text
specmatic.yaml
scripts/run_specmatic_tests.ps1
scripts/run_specmatic_stub.ps1
scripts/run_backward_compatibility_check.ps1
package.json
.github/workflows/test.yml
```

I’ll explain each of these as we go.

## 1:45 - 3:00 | Explaining The Contract

Now let’s look at the contract file:

```text
contracts/clara_api.yaml
```

This file defines the API endpoints Clara supports.

The endpoints covered are:

```text
GET /
GET /health
GET /api/status
GET /chat/{message}
```

The root endpoint, `GET /`, is a simple health check. It returns:

```json
{
  "message": "CLARA is alive"
}
```

The `/health` endpoint returns more detailed status information, like the API version, whether the conversation manager is available, and a timestamp.

The `/api/status` endpoint returns API-level information.

The main conversational endpoint is:

```text
GET /chat/{message}
```

This endpoint accepts a message in the path and returns Clara’s response.

The contract also defines success and error responses. For example, `/chat/{message}` has examples for:

```text
200 success
400 empty-message error
500 internal-server error
```

This is important because Specmatic uses these examples to generate real tests.

So the contract is not only saying “this is what the API looks like.” It is also saying “these are the exact behaviors that must work.”

## 3:00 - 4:15 | Why Contract-Test Mode Was Added

Clara normally uses a real conversation system.

That includes:

```text
ConversationManager
AI processing
memory
tools
Google Calendar
Gmail
tokens and credentials
```

Those are useful in production, but they are not ideal for contract testing.

If contract tests depended on real Gmail tokens or model downloads, the tests would become slow and unreliable.

So I added a contract-test mode in `main.py`.

The key environment variable is:

```powershell
CLARA_CONTRACT_TEST_MODE=1
```

When this is set, Clara still runs as a real FastAPI application, but it uses a deterministic test conversation manager.

That means the HTTP API is real, but the expensive or external AI internals are replaced with predictable responses.

This makes Specmatic tests stable, fast, and safe to run in CI.

## 4:15 - 5:20 | Running Smoke Tests

Before running Specmatic, I first run the basic Python smoke tests.

These are not the main contract tests. They simply check that the FastAPI app loads and the basic endpoints behave correctly.

From the project root, I run:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The expected result is:

```text
5 passed
```

These tests confirm that Clara can start, the health endpoints respond, the chat endpoint returns a normalized response, and errors are structured correctly.

Now that the app-level smoke tests pass, I can move to Specmatic.

## 5:20 - 7:15 | Running Specmatic Contract Tests

Now I’ll run the actual Specmatic provider contract tests.

The script is:

```text
scripts/run_specmatic_tests.ps1
```

I run it with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_specmatic_tests.ps1
```

This script does a few things automatically.

First, it sets:

```powershell
CLARA_CONTRACT_TEST_MODE=1
```

Then it starts Clara locally at:

```text
http://127.0.0.1:8000
```

Next, it waits for the `/health` endpoint to respond, so we know the API is ready.

Then it runs this Specmatic command:

```powershell
npx specmatic test contracts/clara_api.yaml --testBaseURL=http://127.0.0.1:8000
```

Specmatic reads the OpenAPI contract and calls the real Clara API.

It checks whether the real API matches the contract.

For example, it checks:

```text
GET / returns the correct 200 response
GET /health returns the correct health shape
GET /api/status returns the correct API status shape
GET /chat/{message} returns a valid 200 response
GET /chat/__blank__ returns a 400 error
GET /chat/raise error returns a 500 error
```

At the end, the expected result is:

```text
Tests run: 6
Successes: 6
Failures: 0
100% API Coverage
```

This proves that the live Clara provider follows the executable contract.

So this is the first major Specmatic feature: contract testing.

## 7:15 - 8:45 | Service Virtualization

Next, I’ll show service virtualization.

Service virtualization means Specmatic can pretend to be Clara using only the contract.

This is very useful because another developer, frontend app, integration, or AI coding agent can call Clara’s API without starting the real backend.

The script is:

```text
scripts/run_specmatic_stub.ps1
```

I run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_specmatic_stub.ps1
```

This starts the virtual Clara API at:

```text
http://127.0.0.1:9000
```

Now, in another terminal, I can call:

```powershell
curl http://127.0.0.1:9000/
```

I can also call:

```powershell
curl http://127.0.0.1:9000/health
```

And:

```powershell
curl "http://127.0.0.1:9000/chat/What%20time%20is%20my%20next%20meeting"
```

These responses come from Specmatic, not from the real Clara backend.

This means the contract itself can simulate the API.

That reduces integration uncertainty because clients can start building against the API contract immediately.

They do not need real Gmail credentials, Google Calendar access, AI models, ChromaDB, or Clara’s complete runtime.

This is the second major Specmatic feature: service virtualization.

## 8:45 - 10:00 | Backward Compatibility Checking

The third feature is backward compatibility checking.

This protects Clara from accidental breaking API changes.

The script is:

```text
scripts/run_backward_compatibility_check.ps1
```

I run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_backward_compatibility_check.ps1
```

Internally, this runs:

```powershell
npx specmatic backward-compatibility-check --repo-dir=. --base-branch=origin/main --target-path=contracts/clara_api.yaml
```

This compares the current contract with the contract on the base branch.

It helps detect breaking changes like:

```text
removing an endpoint
removing a response field
changing a field type
removing a response status
changing a path
```

For example, if an existing client expects the `response` field from `/chat/{message}`, and I remove that field from the contract, that could break the client.

The compatibility check helps catch that before the change is merged.

If nothing changed in the contract, Specmatic may say:

```text
No specs were changed, skipping the check.
```

That is fine. It means there was nothing new to compare.

I also saved a baseline copy here:

```text
contracts/history/clara_api_v1.yaml
```

That is useful for human review and release tracking.

This is the third major Specmatic feature: backward compatibility checking.

## 10:00 - 11:00 | CI/CD Workflow

I also added a GitHub Actions workflow.

The file is:

```text
.github/workflows/test.yml
```

This runs automatically on push or pull request.

The CI pipeline does the following:

```text
1. Checks out the repository
2. Installs Python
3. Installs Node.js
4. Installs Python dependencies
5. Installs Specmatic
6. Runs pytest smoke tests
7. Runs Specmatic backward compatibility check
8. Starts Clara in contract-test mode
9. Runs Specmatic provider contract tests
10. Starts the Specmatic stub and checks service virtualization
```

This means every pull request can automatically prove that Clara’s API is still contract-compliant.

That is useful not only for humans, but also for AI coding agents, because the contract gives agents a clear boundary and the CI workflow checks whether they broke it.

## 11:00 - 11:40 | Quick Command Recap

Here are the main commands.

Go to the project:

```powershell
cd "D:\Projects\CLARA - Copy"
```

Run smoke tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run Specmatic contract tests:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_specmatic_tests.ps1
```

Run service virtualization:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_specmatic_stub.ps1
```

Run backward compatibility check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_backward_compatibility_check.ps1
```

You can also use npm commands:

```powershell
npm run test:contract
npm run stub
npm run virtualize
npm run compatibility
```

## 11:40 - 12:00 | Closing

To summarize, Clara now has a Specmatic-based executable contract workflow.

Contract testing checks the real Clara API.

Service virtualization creates a fake Clara API from the contract.

Backward compatibility checking protects existing clients from breaking changes.

Together, these make Clara’s API more reliable, easier to integrate with, and easier for both humans and AI coding agents to understand.

That completes the walkthrough.
