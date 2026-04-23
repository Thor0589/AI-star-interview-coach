import os
import time
from collections import defaultdict, deque
from typing import Any, Deque

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DEFAULT_MODEL = "gemini-1.5-pro-latest"
DEFAULT_TIMEOUT_SECONDS = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))
DEFAULT_RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
DEFAULT_BODY_LIMIT_BYTES = int(os.getenv("REQUEST_BODY_LIMIT_BYTES", str(1024 * 1024)))

ALLOWED_MODELS = {
    model.strip()
    for model in os.getenv("GEMINI_ALLOWED_MODELS", DEFAULT_MODEL).split(",")
    if model.strip()
}

CORS_ALLOWLIST = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWLIST",
        "http://localhost:8501,http://127.0.0.1:8501,http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

app = FastAPI(title="Gemini Proxy", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWLIST,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

_REQUEST_BUCKETS: dict[str, Deque[float]] = defaultdict(deque)


class GeminiProxyRequest(BaseModel):
    model: str = Field(default=DEFAULT_MODEL)
    contents: list[dict[str, Any]]
    generationConfig: dict[str, Any] | None = None


@app.middleware("http")
async def request_limits(request: Request, call_next):
    body = await request.body()
    if len(body) > DEFAULT_BODY_LIMIT_BYTES:
        return JSONResponse(
            status_code=413,
            content={"error": {"code": "REQUEST_TOO_LARGE", "message": "Request body exceeds 1 MB limit."}},
        )

    ip = (request.client.host if request.client else "unknown")
    now = time.time()
    window_start = now - 60
    bucket = _REQUEST_BUCKETS[ip]
    while bucket and bucket[0] < window_start:
        bucket.popleft()

    if len(bucket) >= DEFAULT_RATE_LIMIT_PER_MINUTE:
        return JSONResponse(
            status_code=429,
            content={"error": {"code": "RATE_LIMITED", "message": "Rate limit exceeded. Try again later."}},
        )

    bucket.append(now)
    return await call_next(request)


@app.get("/api/health")
async def health():
    return {"status": "ok", "geminiConfigured": bool(API_KEY)}


@app.post("/api/gemini")
async def proxy_gemini(payload: GeminiProxyRequest):
    if not API_KEY:
        return JSONResponse(
            status_code=503,
            content={"error": {"code": "GEMINI_NOT_CONFIGURED", "message": "Gemini service is not configured on the server."}},
        )

    if payload.model not in ALLOWED_MODELS:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "MODEL_NOT_ALLOWED",
                    "message": f"Model '{payload.model}' is not allowed by server configuration.",
                }
            },
        )

    upstream_url = f"https://generativelanguage.googleapis.com/v1beta/models/{payload.model}:generateContent"
    request_body = {"contents": payload.contents}
    if payload.generationConfig:
        request_body["generationConfig"] = payload.generationConfig

    headers = {"Content-Type": "application/json", "x-goog-api-key": API_KEY}

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
            upstream = await client.post(upstream_url, headers=headers, json=request_body)
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=504,
            content={"error": {"code": "UPSTREAM_TIMEOUT", "message": "Gemini upstream timed out."}},
        )
    except Exception:
        return JSONResponse(
            status_code=502,
            content={"error": {"code": "UPSTREAM_UNAVAILABLE", "message": "Gemini upstream unavailable."}},
        )

    try:
        upstream_json = upstream.json()
    except Exception:
        return JSONResponse(
            status_code=502,
            content={"error": {"code": "UPSTREAM_BAD_RESPONSE", "message": "Gemini returned a non-JSON response."}},
        )

    if upstream.status_code >= 400:
        err_msg = upstream_json.get("error", {}).get("message", "Gemini request failed.")
        return JSONResponse(
            status_code=upstream.status_code,
            content={"error": {"code": "GEMINI_ERROR", "message": err_msg}},
        )

    return JSONResponse(status_code=200, content=upstream_json)
