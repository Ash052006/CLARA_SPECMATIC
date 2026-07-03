# Clara Specmatic Docker Guide

This guide explains how the Dockerized Clara + Specmatic setup works, how to use it, and how to test every workflow.

## What This Docker Setup Proves

The Docker setup proves that Clara's contract workflows are reproducible outside the developer's local Windows environment.

It covers:

1. FastAPI smoke tests in Docker
2. Specmatic provider contract testing in Docker
3. Specmatic service virtualization in Docker
4. Specmatic backward compatibility checks in Docker

This is useful for reviewers because they can run the project with Docker instead of manually configuring Python, Node.js, Java, Specmatic, or local virtual environments.

## Main Docker Files

```text
Dockerfile
```

Builds a lightweight image for Clara's Specmatic workflows.

```text
docker-compose.yml
```

Defines runnable services for Clara, Specmatic tests, virtualized stubs, compatibility checks, and smoke tests.

```text
requirements.docker.txt
```

Installs only the lightweight Python dependencies needed for contract-test mode.

```text
.dockerignore
```

Keeps secrets, virtual environments, node_modules, generated reports, and local files out of the Docker build context.

## Why Docker Uses Contract-Test Mode

Clara's real runtime can involve AI models, Gmail, Google Calendar, ChromaDB, memory, and credentials.

For contract testing, those dependencies are not necessary. The purpose is to prove the HTTP API follows the executable contract.

So Docker sets:

```text
CLARA_CONTRACT_TEST_MODE=1
```

In this mode:

- Clara still runs as a real FastAPI HTTP API.
- Specmatic still calls real endpoints.
- The expensive AI and Google integrations are replaced with deterministic test responses.
- No credentials are required.
- The Docker build stays practical and review-friendly.

## Docker Services

### clara-api

Runs Clara on port `8000`.

```bash
docker compose up clara-api
```

Health check:

```text
http://localhost:8000/health
```

### smoke-tests

Runs the Python FastAPI smoke tests inside Docker.

```bash
docker compose run --rm smoke-tests
```

Expected result:

```text
5 passed
```

### specmatic-test

Starts Clara, waits for it to become healthy, then runs Specmatic provider contract tests.

```bash
docker compose run --rm specmatic-test
```

Expected result:

```text
Tests run: 6
Successes: 6
Failures: 0
100% API Coverage
```

### specmatic-stub

Starts a virtual Clara API from the contract on port `9000`.

```bash
docker compose up -d specmatic-stub
```

Test it:

```bash
curl http://localhost:9000/
curl http://localhost:9000/health
curl "http://localhost:9000/chat/What%20time%20is%20my%20next%20meeting"
```

### compatibility

Runs the Specmatic backward compatibility check.

```bash
docker compose run --rm compatibility
```

If no contract changes exist compared to the base branch, Specmatic prints:

```text
No specs were changed, skipping the check.
```

That is an acceptable pass for the current unchanged contract.

## Full Verification Sequence

Run these commands from the project root:

```bash
cd "D:\Projects\CLARA - Copy"
```

Build the image:

```bash
docker compose build
```

Run smoke tests:

```bash
docker compose run --rm smoke-tests
```

Run provider contract tests:

```bash
docker compose run --rm specmatic-test
```

Run compatibility check:

```bash
docker compose run --rm compatibility
```

Start service virtualization:

```bash
docker compose up -d specmatic-stub
```

Call the virtual service:

```bash
curl http://localhost:9000/
```

Stop Docker services:

```bash
docker compose down
```

## Verified Results

The Docker setup was verified with these results:

```text
docker compose build
Result: passed

Docker smoke tests
Result: 5 passed

Docker Specmatic provider tests
Result: 6 tests, 6 successes, 0 failures, 100% API coverage

Docker backward compatibility check
Result: passed; no changed specs to compare

Docker Specmatic stub
Result: started successfully and returned a contract-valid response
```

## Why This Is Valuable

This setup gives Clara a professional API delivery workflow:

- The contract is executable, not just documentation.
- The real provider is tested against the contract.
- Consumers can use a stub before the real API is available.
- Backward compatibility checks reduce breaking changes.
- Docker makes the setup reproducible for reviewers and CI systems.

For an internship evaluation, this shows practical understanding of API reliability, contract-driven development, CI readiness, and integration testing.
