import os
from dataclasses import dataclass
from typing import Any

import requests

DEFAULT_PROXY_BASE_URL = os.getenv("GEMINI_PROXY_BASE_URL", "http://localhost:8000")
DEFAULT_PROXY_MODEL = os.getenv("GEMINI_PROXY_MODEL", "gemini-1.5-pro-latest")
DEFAULT_PROXY_TIMEOUT_SECONDS = int(os.getenv("GEMINI_PROXY_TIMEOUT_SECONDS", "30"))


@dataclass
class ProxyResponse:
    ok: bool
    status_code: int
    reason: str
    text: str
    _json: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self._json


def safe_gemini_post(url=None, headers=None, json=None, timeout=30, **kwargs):
    payload = json or {}
    request_body = {
        "model": DEFAULT_PROXY_MODEL,
        "contents": payload.get("contents", []),
    }
    if payload.get("generationConfig"):
        request_body["generationConfig"] = payload["generationConfig"]

    try:
        response = requests.post(
            f"{DEFAULT_PROXY_BASE_URL}/api/gemini",
            json=request_body,
            timeout=timeout or DEFAULT_PROXY_TIMEOUT_SECONDS,
        )
        response_json = response.json() if response.content else {}
        return ProxyResponse(
            ok=response.ok,
            status_code=response.status_code,
            reason=response.reason,
            text=response.text,
            _json=response_json,
        )
    except requests.exceptions.Timeout:
        return ProxyResponse(
            ok=False,
            status_code=504,
            reason="Gateway Timeout",
            text="Gemini proxy timeout",
            _json={"error": {"message": "Gemini proxy timeout"}},
        )
    except Exception:
        return ProxyResponse(
            ok=False,
            status_code=502,
            reason="Bad Gateway",
            text="Gemini proxy unavailable",
            _json={"error": {"message": "Gemini proxy unavailable"}},
        )


def get_proxy_health() -> dict[str, Any]:
    try:
        response = requests.get(f"{DEFAULT_PROXY_BASE_URL}/api/health", timeout=5)
        return response.json() if response.content else {"status": "error", "geminiConfigured": False}
    except Exception:
        return {"status": "error", "geminiConfigured": False}
