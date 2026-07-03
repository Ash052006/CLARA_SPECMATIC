# Clara API Contract

Clara's provider contract is `contracts/clara_api.yaml`. It is an OpenAPI 3.0 document with named examples that Specmatic turns into executable provider tests and stub responses.

## Specmatic Workflows

### Contract Testing

`npx specmatic test contracts/clara_api.yaml --testBaseURL=http://127.0.0.1:8000` verifies the real FastAPI provider against the contract.

### Service Virtualization

`npx specmatic stub contracts/clara_api.yaml --host=127.0.0.1 --port=9000` starts a virtual Clara service from the contract. This lets consumers and AI agents integrate against Clara's boundary without needing Clara's runtime dependencies.

### Backward Compatibility

`npx specmatic backward-compatibility-check --repo-dir=. --base-branch=origin/main --target-path=contracts/clara_api.yaml` checks contract changes against the base branch.

## Contract-Test Runtime

Set `CLARA_CONTRACT_TEST_MODE=1` when running provider contract tests. This swaps the heavy model and Google-backed conversation manager for a deterministic provider while preserving FastAPI routing, middleware, response normalization, and error handling.

## Endpoints

### GET /

```json
{
  "message": "CLARA is alive"
}
```

### GET /health

```json
{
  "status": "ok",
  "version": "1.0.0",
  "conversation_manager": "available",
  "timestamp": "2026-06-29T12:00:00+00:00"
}
```

### GET /api/status

```json
{
  "api": "Clara",
  "version": "1.0.0",
  "status": "ok",
  "timestamp": "2026-06-29T12:00:00+00:00"
}
```

### GET /chat/{message}

```json
{
  "response": "Contract test response for: What time is my next meeting",
  "timestamp": "2026-06-29T12:00:00+00:00",
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "plan": [],
  "tools": [],
  "execution": [],
  "memory": {},
  "preferences": {},
  "long_term": {}
}
```

## Error Format

```json
{
  "error_code": "EMPTY_MESSAGE",
  "message": "Message must contain at least one non-space character.",
  "details": {
    "parameter": "message"
  }
}
```
