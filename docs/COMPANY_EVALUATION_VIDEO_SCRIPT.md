# Clara + Specmatic + Docker - 12 Minute Evaluation Video Script

## Goal Of The Video

Use this script to explain the project clearly to an evaluator. The video should show that Clara is not just a FastAPI app, but an API with executable contracts, automated provider validation, service virtualization, backward compatibility checks, and Dockerized reproducibility.

## 0:00 - 0:45 | Opening

Hi, my name is [Your Name], and in this walkthrough I'll present my Specmatic integration for CLARA.

CLARA, which stands for Contextual Learning and Autonomous Response Assistant, is my FastAPI-based conversational AI assistant. The long-term vision is to build an intelligent assistant that can understand natural language, maintain conversation context, remember user preferences, reason about user requests, and interact with external services like Gmail and Google Calendar through the Model Context Protocol (MCP).

The project follows a modular architecture with components for conversation management, memory, reasoning, and external tool execution. This design allows new capabilities to be added without changing the public API.

For this task, my goal wasn't to demonstrate the AI features themselves, but to improve the reliability of CLARA's API using executable contracts. I implemented provider contract testing, service virtualization, and backward compatibility checking using Specmatic, and Dockerized the complete workflow so it can be reproduced consistently on any machine.

## 0:45 - 1:45 | What Clara Does

At a high level, CLARA exposes REST APIs that act as the entry point to the assistant.

The primary endpoint is:
```text
GET /chat/{message}
```

A client sends a natural language message, and CLARA processes it through its conversation layer before returning a structured response. In the complete system, this processing can involve AI reasoning, memory retrieval, and integrations with external tools such as Gmail or Google Calendar.

CLARA also exposes supporting endpoints:

```text
GET /
GET /health
GET /api/status
```

These endpoints are useful for service discovery, deployment verification, health monitoring, and automated testing.

As CLARA grows and more clients integrate with its APIs, maintaining a stable API contract becomes critical. Any accidental change to request or response formats could break downstream applications. That's where Specmatic becomes valuable—it turns the OpenAPI specification into an executable contract that continuously validates the API implementation.

## 1:45 - 2:45 | What Specmatic Adds

Specmatic lets an OpenAPI contract become executable.

Instead of treating the OpenAPI file as passive documentation, Specmatic uses it to run real checks.

In this project, Specmatic is used for three things:

```text
1. Contract testing
2. Service virtualization
3. Backward compatibility checking
```

Contract testing checks whether the real Clara API follows the OpenAPI contract.

Service virtualization creates a fake Clara API from the contract, so consumers can integrate without running the full backend.

Backward compatibility checking helps detect contract changes that could break existing clients.

This makes the API boundary clearer for humans, downstream services, and AI coding agents.

## 2:45 - 3:45 | The Executable Contract

The main contract file is:

```text
contracts/clara_api.yaml
```

This is an OpenAPI 3 contract.

It describes Clara’s API paths, methods, parameters, response schemas, and examples.

The endpoints in the contract are:

```text
GET /
GET /health
GET /api/status
GET /chat/{message}
```

For the chat endpoint, the contract includes examples for:

```text
200 success
400 empty-message error
500 internal-server error
```

These examples are important because Specmatic uses them as executable scenarios.

So the contract is not only saying what the API should look like. It is also becoming the test source for the API.

## 3:45 - 4:45 | Contract-Test Mode In Clara

Clara’s real runtime can involve AI models, Gmail, Google Calendar, memory, and tokens.

Those dependencies are not ideal for contract testing because they can be slow, flaky, or require credentials.

So I added a contract-test mode in `main.py`.

The key environment variable is:

```text
CLARA_CONTRACT_TEST_MODE=1
```

When this is enabled, Clara still runs as a real FastAPI HTTP service, but it uses a deterministic test conversation manager.

This means Specmatic tests the real HTTP routing, response normalization, error handling, and schemas, without needing external credentials or model downloads.

This is a deliberate design choice: contract tests should verify the API boundary, not depend on unrelated external services.

## 4:45 - 5:45 | Local Specmatic Provider Testing

The local provider contract test script is:

```text
scripts/run_specmatic_tests.ps1
```

It starts Clara on:

```text
http://127.0.0.1:8000
```

Then it runs:

```text
npx specmatic test contracts/clara_api.yaml --testBaseURL=http://127.0.0.1:8000
```

Specmatic calls the real Clara API and checks the responses against the contract.

The verified result is:

```text
Tests run: 6
Successes: 6
Failures: 0
100% API Coverage
```

This proves that the live Clara provider is contract-compliant.

## 5:45 - 6:45 | Service Virtualization

The second workflow is service virtualization.

The script is:

```text
scripts/run_specmatic_stub.ps1
```

It starts a virtual Clara API on:

```text
http://127.0.0.1:9000
```

This virtual API is created from the OpenAPI contract.

That means a frontend developer, another backend service, or even an AI coding agent can call Clara’s API before the real implementation is running.

This reduces integration uncertainty because consumers do not need Gmail tokens, Google Calendar setup, ChromaDB, or the AI model stack just to start integration work.

The contract itself becomes a runnable API simulation.

## 6:45 - 7:45 | Backward Compatibility

The third workflow is backward compatibility checking.

The script is:

```text
scripts/run_backward_compatibility_check.ps1
```

It runs:

```text
npx specmatic backward-compatibility-check --repo-dir=. --base-branch=origin/main --target-path=contracts/clara_api.yaml
```

This checks whether the current contract introduces breaking changes compared to the base branch.

Examples of breaking changes include:

```text
removing an endpoint
changing a response field type
removing a required response field
removing a status code
changing an existing path
```

This matters because APIs often fail not because the server crashes, but because a client’s expectation silently changes. The compatibility check helps catch that risk early.

## 7:45 - 8:45 | Why I Added Docker

I also added Docker support because a reviewer should be able to run this project without reproducing my exact local environment.

The Docker setup includes:

```text
Dockerfile
docker-compose.yml
.dockerignore
requirements.docker.txt
```

The Docker image installs Python, Node.js, Java, Specmatic, and the lightweight FastAPI dependencies needed for contract-test mode.

Java is included because the Specmatic npm package runs the Specmatic jar internally.

The Docker setup avoids installing heavy AI dependencies because Docker is meant to validate the API contract workflows, not run the full AI production stack.

## 8:45 - 10:15 | Docker Commands And Verification

The first Docker command is:

```text
docker compose build
```

This builds the Clara Specmatic image.

Then I can run the smoke tests:

```text
docker compose run --rm smoke-tests
```

This passed with:

```text
5 passed
```

Next, I run Specmatic provider contract testing in Docker:

```text
docker compose run --rm specmatic-test
```

This starts the Dockerized Clara API, waits for it to become healthy, and runs Specmatic against it.

The verified result was:

```text
Tests run: 6
Successes: 6
Failures: 0
100% API Coverage
```

Then I run backward compatibility:

```text
docker compose run --rm compatibility
```

This successfully ran inside Docker. Since the current contract had no changed spec compared to the base, Specmatic reported that no specs were changed.

Finally, I run service virtualization in Docker:

```text
docker compose up -d specmatic-stub
```

Then I test it with:

```text
curl http://localhost:9000/
```

The Dockerized stub returned a contract-valid response, proving service virtualization works in Docker too.

## 10:15 - 11:00 | CI And Reviewability

The project also includes GitHub Actions configuration.

The CI workflow installs dependencies, runs smoke tests, runs the compatibility check, starts Clara, runs Specmatic provider tests, and checks service virtualization.

With Docker added, the project is easier to evaluate because the reviewer can use Compose commands instead of manually setting up Python, Node, Java, and Specmatic.

This is important from a software engineering perspective because the deliverable is reproducible.

## 11:00 - 11:40 | Key Engineering Decisions

There are a few design decisions I want to highlight.

First, the OpenAPI contract is treated as the source of truth.

Second, contract tests are deterministic and do not depend on external APIs or secrets.

Third, service virtualization allows parallel development between Clara and its consumers.

Fourth, backward compatibility checking protects existing clients from accidental breaking changes.

Fifth, Docker makes the whole workflow portable and reviewer-friendly.

Together, these decisions improve API reliability and reduce integration risk.

## 11:40 - 12:00 | Closing

To summarize, Clara now has a complete Specmatic workflow.

It supports provider contract testing, service virtualization, backward compatibility checking, and Dockerized execution.

This turns the API contract into an executable asset. It helps humans understand the API, helps services integrate safely, and gives AI coding agents a clear boundary to work within.

That completes my walkthrough of the Clara Specmatic integration.

## Command Cheat Sheet For The Video

```text
docker compose build
```

```text
docker compose run --rm smoke-tests
```

```text
docker compose run --rm specmatic-test
```

```text
docker compose run --rm compatibility
```

```text
docker compose up -d specmatic-stub
```

```text
curl http://localhost:9000/
```

```text
docker compose down
```
