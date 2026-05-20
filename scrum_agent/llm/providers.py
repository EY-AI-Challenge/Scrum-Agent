"""Configurable LLM provider layer for the Scrum Agent.

The providers return text only. The orchestrator owns JSON parsing, schema
validation, and fallback so LLM output can never silently mutate the core plan.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


DEFAULT_OLLAMA_MODEL = "llama3.2:3b"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OPENAI_MODEL = "gpt-5.5"
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"


@dataclass
class LLMResponse:
    provider: str
    model: str
    content: str
    fallback_used: bool = False
    latency_ms: int = 0
    error: str | None = None


class LLMProvider(Protocol):
    provider_name: str
    model: str

    def generate(
        self,
        system_prompt: str,
        user_payload: dict,
        response_format: str = "json",
    ) -> LLMResponse:
        """Generate a response for the Scrum Agent orchestrator."""


class NullProvider:
    provider_name = "null"
    model = "offline-deterministic"

    def generate(
        self,
        system_prompt: str,
        user_payload: dict,
        response_format: str = "json",
    ) -> LLMResponse:
        return LLMResponse(
            provider=self.provider_name,
            model=self.model,
            content="",
            fallback_used=True,
            latency_ms=0,
            error="LLM disabled; deterministic fallback used.",
        )


class OllamaProvider:
    provider_name = "ollama"

    def __init__(self, base_url: str | None = None, model: str | None = None, timeout_seconds: int | None = None):
        self.base_url = (base_url or os.getenv("SCRUM_AGENT_LLM_BASE_URL") or DEFAULT_OLLAMA_BASE_URL).rstrip("/")
        self.model = model or os.getenv("SCRUM_AGENT_LLM_MODEL") or DEFAULT_OLLAMA_MODEL
        self.timeout_seconds = timeout_seconds or _env_int("SCRUM_AGENT_LLM_TIMEOUT_SECONDS", 120)

    def generate(
        self,
        system_prompt: str,
        user_payload: dict,
        response_format: str = "json",
    ) -> LLMResponse:
        started = time.perf_counter()
        request_payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            "options": {
                "temperature": 0.2,
                "num_ctx": _env_int("SCRUM_AGENT_LLM_NUM_CTX", 4096),
                "num_predict": _env_int("SCRUM_AGENT_LLM_NUM_PREDICT", 700),
            },
        }
        if response_format == "json":
            request_payload["format"] = "json"

        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(request_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_body = json.loads(response.read().decode("utf-8"))
            content = response_body.get("message", {}).get("content", "")
            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=content,
                latency_ms=_elapsed_ms(started),
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content="",
                fallback_used=True,
                latency_ms=_elapsed_ms(started),
                error=str(exc),
            )


class OpenAIProvider:
    provider_name = "openai"

    def __init__(self, base_url: str | None = None, model: str | None = None, timeout_seconds: int | None = None):
        self.base_url = (base_url or os.getenv("SCRUM_AGENT_OPENAI_BASE_URL") or DEFAULT_OPENAI_BASE_URL).rstrip("/")
        self.model = model or os.getenv("SCRUM_AGENT_LLM_MODEL") or DEFAULT_OPENAI_MODEL
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.timeout_seconds = timeout_seconds or _env_int("SCRUM_AGENT_LLM_TIMEOUT_SECONDS", 120)

    def generate(
        self,
        system_prompt: str,
        user_payload: dict,
        response_format: str = "json",
    ) -> LLMResponse:
        started = time.perf_counter()
        if not self.api_key:
            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content="",
                fallback_used=True,
                latency_ms=0,
                error="OPENAI_API_KEY is not configured.",
            )

        request_payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            "temperature": 0.2,
        }
        if response_format == "json":
            request_payload["response_format"] = {"type": "json_object"}

        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(request_payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_body = json.loads(response.read().decode("utf-8"))
            content = response_body.get("choices", [{}])[0].get("message", {}).get("content", "")
            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=content,
                latency_ms=_elapsed_ms(started),
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, KeyError) as exc:
            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content="",
                fallback_used=True,
                latency_ms=_elapsed_ms(started),
                error=str(exc),
            )


def provider_from_env(mode: str = "auto") -> LLMProvider:
    configured_provider = os.getenv("SCRUM_AGENT_LLM_PROVIDER", "").strip().lower()
    selected = configured_provider or mode
    if selected == "auto":
        selected = "ollama"
    if selected == "ollama":
        return OllamaProvider()
    if selected == "openai":
        return OpenAIProvider()
    return NullProvider()


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def _env_int(name: str, fallback: int) -> int:
    try:
        return int(os.getenv(name, str(fallback)))
    except ValueError:
        return fallback
