# Clara Developer Guide

This guide explains how to start the API locally, how the main functions work, and how to test each part of the project from the command line.

## 1. Prerequisites

Install Python dependencies and test tooling:

```powershell
python -m pip install -r requirements.txt
npm install
```

If a local virtual environment exists, the provided scripts will prefer `.venv/Scripts/python.exe` automatically.

## 2. Start the API locally

From the repository root, run:

```powershell
make run
```

That starts the FastAPI app with:

```powershell
uvicorn main:app --reload
```

The app is available at:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/api/status
- http://127.0.0.1:8000/chat/{message}

## 3. Main endpoints and behavior

### GET /
Returns a simple health message.

```powershell
curl http://127.0.0.1:8000/
```

### GET /health
Returns the health state of the application.

```powershell
curl http://127.0.0.1:8000/health
```

### GET /api/status
Returns the API status payload.

```powershell
curl http://127.0.0.1:8000/api/status
```

### GET /chat/{message}
Processes a message and returns a normalized response.

```powershell
curl "http://127.0.0.1:8000/chat/What%20time%20is%20my%20next%20meeting"
```

Blank or whitespace-only input returns HTTP 400 with `EMPTY_MESSAGE`.

## 4. How the main functions work

### `main.py`

#### `utc_timestamp()`
Creates the current UTC timestamp used in API responses.

#### `build_conversation_manager()`
Selects the conversation manager implementation:

- returns a deterministic contract-test stub when `CLARA_CONTRACT_TEST_MODE=1`
- returns `None` when `CLARA_SKIP_CONVERSATION_MANAGER=1`
- otherwise loads the real conversation manager from the brain layer

#### `error_response(error_code, message, details=None)`
Builds a consistent JSON error body.

#### `normalize_chat_response(raw_response)`
Ensures the chat response contains the required fields and adds defaults when missing.

#### `home()`
Handles `GET /`.

#### `health()`
Handles `GET /health`.

#### `api_status()`
Handles `GET /api/status`.

#### `chat(message)`
Handles `GET /chat/{message}`. It validates the message, returns `400` for blank input, returns `503` if the conversation manager is unavailable, and otherwise returns the normalized response.

## 5. Testing commands

### Run smoke tests

```powershell
pytest
```

or:

```powershell
make test-smoke
```

### Run the full test target

```powershell
make test
```

This runs the smoke suite, Specmatic contract tests, and the backward compatibility check.

### Run contract tests

```powershell
make test-contract
```

This runs the PowerShell wrapper:

```powershell
scripts/run_specmatic_tests.ps1
```

The script starts the app on port `8000`, waits for `/health`, and then runs Specmatic against `contracts/clara_api.yaml`.

### Run the Specmatic stub/mock server

```powershell
make stub
```

or:

```powershell
npx specmatic stub contracts/clara_api.yaml --host=127.0.0.1 --port=9000
```

### Run backward compatibility checks

```powershell
make compatibility
```

or:

```powershell
npx specmatic backward-compatibility-check --repo-dir=. --base-branch=origin/main --target-path=contracts/clara_api.yaml
```

### Run resilience-style contract checks

```powershell
make resilience
```

or:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_resilience_tests.ps1
```

This workflow starts the FastAPI app in contract-test mode and runs Specmatic contract tests against the live API. It is intended as a lightweight resilience check for the contract boundary, similar to the schema-resiliency-testing pattern from Specmatic Labs.

## 6. Where to write tests

### Python API tests
Add new API tests in `tests/test_api.py`.

Current smoke tests cover:

- root endpoint
- health endpoint
- chat success path
- blank-message validation
- unhandled server errors

### Fixtures
Shared test fixtures should go in `tests/conftest.py`.

### Contract tests
The OpenAPI contract lives in `contracts/clara_api.yaml`.

Inline examples are already defined there, and external examples are stored in `contracts/clara_api_examples`.

## 7. Recommended development flow

1. Start the app:

   ```powershell
   make run
   ```

2. In another terminal, run smoke tests:

   ```powershell
   pytest
   ```

3. Run contract tests:

   ```powershell
   make test-contract
   ```

4. If you need a contract-backed mock for an external consumer, start the stub:

   ```powershell
   make stub
   ```

## 8. Contract-first workflow

Before changing an endpoint:

1. Update the OpenAPI contract and examples.
2. Run the backward compatibility check.
3. Run the Specmatic stub if consumers need the new behavior before Clara is implemented.
4. Implement the FastAPI change.
5. Run pytest smoke tests and Specmatic provider tests.

## 9. Backward compatibility

Run the compatibility check before merging contract changes. Removing fields, changing field types, renaming paths, or changing status codes is breaking. Prefer additive optional fields or versioned endpoints.

A baseline version of the current contract is stored at `contracts/history/clara_api_v1.yaml`.

## 10. Secrets

Do not commit `credentials.json`, `token.json`, `gmail_token.json`, `.env.local`, or `.env.test`. Specmatic tests should run without Google credentials or model downloads by using `CLARA_CONTRACT_TEST_MODE=1`.

## 11. Before committing

```powershell
pytest
npx specmatic backward-compatibility-check --repo-dir=. --base-branch=origin/main --target-path=contracts/clara_api.yaml
npx specmatic test contracts/clara_api.yaml --testBaseURL=http://127.0.0.1:8000
```
