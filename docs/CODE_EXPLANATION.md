# Clara Code Explanation

This document explains the main parts of the Clara project, how the code is organized, and how the Specmatic integration fits into the application.

## 1. Project purpose

Clara is a FastAPI-based conversational AI application. Its job is to receive a user message, process it through the conversation stack, and return a structured response.

The project also includes contract-driven development tooling so the API can be tested, stubbed, and validated independently of the full runtime.

## 2. Main application entry point

### main.py

This is the core FastAPI application.

It contains:

- the FastAPI app instance
- request/response error handling
- endpoint definitions for `/`, `/health`, `/api/status`, and `/chat/{message}`
- a contract-test mode that replaces the real conversation manager with a deterministic stub

Key functions:

- `utc_timestamp()`
  - Generates the UTC timestamp used in API responses.

- `build_conversation_manager()`
  - Chooses the appropriate conversation manager implementation.
  - In contract-test mode, it returns a simple deterministic test object.
  - If the conversation manager is disabled, it returns `None`.
  - Otherwise it loads the real conversation manager.

- `error_response(error_code, message, details=None)`
  - Builds a consistent JSON error payload.

- `normalize_chat_response(raw_response)`
  - Makes sure the chat response contains standard fields like `response`, `timestamp`, and `conversation_id`.

The HTTP routes are:

- `GET /` → returns a simple alive message
- `GET /health` → returns service health information
- `GET /api/status` → returns API status information
- `GET /chat/{message}` → processes a message and returns a chat response

## 3. Application structure

### brain/

This folder contains the logic for conversation handling and orchestration.

Important files:

- `conversation_manager.py`
  - Responsible for the main conversation flow.

- `llm_manager.py`
  - Handles LLM-related logic.

- `planner.py`
  - Plans the interaction flow.

- `response_generator.py`
  - Generates responses.

- `router.py`
  - Routes work to the right component.

### memory/

Handles short-term, long-term, and preference memory for conversations.

Important files:

- `short_term.py`
- `long_term.py`
- `memory_manager.py`
- `preference.py`
- `context_manager.py`

These modules help the app remember what was discussed and how user preferences should be applied.

### tools/

Contains tool execution logic.

- `executor.py`
- `tool_router.py`

These modules allow the agent to run tools when needed.

### mcp/

Contains Model Context Protocol server adapters and integrations.

- `base_server.py`
- `calendar_server.py`
- `gmail_server.py`
- `google_calendar_server.py`
- `registry.py`

These are used to connect Clara with external systems such as Gmail or calendar tools.

### models/

Contains data schemas used by the application.

- `schemas.py`

### config/

Contains runtime configuration settings.

- `settings.py`

## 4. How the API works at runtime

When a request arrives:

1. FastAPI routes it to the correct endpoint.
2. The endpoint validates the request.
3. The conversation manager is invoked if needed.
4. The response is normalized and returned as JSON.

For `/chat/{message}`:

- the message is trimmed
- empty messages return HTTP 400
- if the conversation manager is unavailable, the endpoint returns HTTP 503
- otherwise a response is generated and normalized

## 5. Why contract testing is included

The repository uses Specmatic so the API contract is executable rather than only descriptive.

This gives three major benefits:

- contract testing for the real API
- service virtualization for consumers and agents
- backward compatibility checks for contract changes

## 6. Specmatic integration

### contracts/

The OpenAPI contract lives in:

- `contracts/clara_api.yaml`

This file defines:

- endpoints
- request parameters
- response schemas
- example responses
- error payloads

### contracts/clara_api_examples/

This directory contains external example files used by Specmatic.

They provide concrete request/response examples for the contract.

### specmatic.yaml

This file tells Specmatic where the API contract is located and how it should be discovered.

## 7. Testing structure

### tests/

The project contains smoke tests for the FastAPI app.

The main test file is:

- `tests/test_api.py`

These tests cover:

- root endpoint behavior
- health endpoint behavior
- chat success handling
- empty-message validation
- internal server error handling

### scripts/

The scripts folder contains helpers for running Specmatic-driven workflows.

- `run_specmatic_tests.ps1`
  - starts the app and runs contract tests

- `run_specmatic_stub.ps1`
  - starts a stub/mock version of the API from the contract

- `run_backward_compatibility_check.ps1`
  - checks whether contract changes break compatibility

- `run_resilience_tests.ps1`
  - runs a resilience-style contract workflow against the live app

## 8. How the project is meant to be developed

A typical workflow is:

1. Update the OpenAPI contract in `contracts/clara_api.yaml`
2. Add or adjust examples in `contracts/clara_api_examples`
3. Implement or adjust the FastAPI behavior in `main.py`
4. Run smoke tests with `pytest`
5. Run contract tests with Specmatic
6. Run compatibility and resilience checks

This keeps the implementation aligned with the contract and reduces surprises for downstream consumers.

## 9. Important design idea

Clara uses executable contracts to create a clear boundary between:

- the implementation
- the API contract
- the consumer experience
- AI-assisted coding and automation workflows

That boundary makes the system easier to reason about and safer to change.

## 10. Summary

The project combines:

- a FastAPI service for the actual application behavior
- a contract-first approach using OpenAPI and Specmatic
- deterministic test mode for stable automated verification
- example-driven testing and service virtualization

This gives Clara a stronger and more reliable development process, especially when working with AI tools or multiple integrations.
