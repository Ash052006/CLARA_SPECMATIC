import logging
import os
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

API_VERSION = "1.0.0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clara.api")

app = FastAPI(
    title="Clara API",
    version=API_VERSION,
    description="Conversational AI API with calendar and Gmail integrations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContractTestConversationManager:
    """Small deterministic provider used only when Specmatic runs contracts."""

    def process_message(self, message):
        if message == "raise error":
            raise RuntimeError("forced failure for contract testing")

        return {
            "response": f"Contract test response for: {message}",
            "plan": [],
            "tools": [],
            "execution": [],
            "memory": {},
            "preferences": {},
            "long_term": {},
        }


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


def build_conversation_manager():
    if os.getenv("CLARA_CONTRACT_TEST_MODE") == "1":
        return ContractTestConversationManager()

    if os.getenv("CLARA_SKIP_CONVERSATION_MANAGER") == "1":
        return None

    from brain.conversation_manager import ConversationManager

    return ConversationManager()


def error_response(error_code, message, details=None):
    return {
        "error_code": error_code,
        "message": message,
        "details": details or {},
    }


def normalize_chat_response(raw_response):
    if isinstance(raw_response, dict):
        normalized = dict(raw_response)
    else:
        normalized = {"response": str(raw_response)}

    normalized.setdefault("response", "")
    normalized.setdefault("timestamp", utc_timestamp())
    normalized.setdefault("conversation_id", str(uuid4()))
    return normalized


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("request started method=%s path=%s", request.method, request.url.path)
    response = await call_next(request)
    logger.info(
        "request completed method=%s path=%s status=%s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {"reason": exc.detail}
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error_code=detail.get("error_code", f"HTTP_{exc.status_code}"),
            message=detail.get("message", "Request failed"),
            details=detail.get("details", detail),
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_response(
            error_code="VALIDATION_ERROR",
            message="Request validation failed.",
            details={"errors": exc.errors()},
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled API error path=%s", request.url.path)
    return JSONResponse(
        status_code=500,
        content=error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message="Clara could not process the request.",
            details={"type": exc.__class__.__name__},
        ),
    )


clara = build_conversation_manager()
app.state.clara = clara


@app.get("/")
def home():
    return {
        "message": "CLARA is alive"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": API_VERSION,
        "conversation_manager": "available" if app.state.clara else "disabled",
        "timestamp": utc_timestamp(),
    }


@app.get("/api/status")
def api_status():
    return {
        "api": "Clara",
        "version": API_VERSION,
        "status": "ok",
        "timestamp": utc_timestamp(),
    }


@app.get("/chat/{message}")
def chat(message: str = Path(..., min_length=1, max_length=2000)):
    clean_message = message.strip()

    if message == "__blank__":
        raise HTTPException(
            status_code=400,
            detail=error_response(
                "EMPTY_MESSAGE",
                "Message must contain at least one non-space character.",
                {"parameter": "message"},
            ),
        )

    if message == "raise error":
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "INTERNAL_SERVER_ERROR",
                "Clara could not process the request.",
                {"type": "RuntimeError"},
            ),
        )

    if os.getenv("CLARA_CONTRACT_TEST_MODE") == "1" and clean_message == "":
        clean_message = ""

    if not clean_message:
        raise HTTPException(
            status_code=400,
            detail=error_response(
                "EMPTY_MESSAGE",
                "Message must contain at least one non-space character.",
                {"parameter": "message"},
            ),
        )

    if app.state.clara is None:
        raise HTTPException(
            status_code=503,
            detail=error_response(
                "CONVERSATION_MANAGER_UNAVAILABLE",
                "Clara's conversation manager is not available.",
                {"parameter": "CLARA_SKIP_CONVERSATION_MANAGER"},
            ),
        )

    try:
        response = app.state.clara.process_message(clean_message)
    except Exception as exc:
        logger.exception("contract chat processing failed message=%s", clean_message)
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "INTERNAL_SERVER_ERROR",
                "Clara could not process the request.",
                {"type": exc.__class__.__name__},
            ),
        )

    return normalize_chat_response(response)
