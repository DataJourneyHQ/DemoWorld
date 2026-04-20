"""
tracer.py — unified logger: Postgres + Confident AI (deepeval).
"""
from __future__ import annotations

import os
import uuid

from db import log_run

_DEEPEVAL_OK = False
try:
    from deepeval.tracing import observe, update_llm_span, trace_manager  # type: ignore
    _DEEPEVAL_OK = bool(os.getenv("CONFIDENT_API_KEY") or os.getenv("DEEPEVAL_API_KEY"))
    if os.getenv("DEEPEVAL_API_KEY") and not os.getenv("CONFIDENT_API_KEY"):
        os.environ["CONFIDENT_API_KEY"] = os.environ["DEEPEVAL_API_KEY"]
except Exception:
    _DEEPEVAL_OK = False


def deepeval_enabled() -> bool:
    return _DEEPEVAL_OK


def log_llm_call(
    *,
    model_id: str,
    model_type: str,
    prompt: str,
    output: str | None,
    error: str | None,
    elapsed_sec: float,
    mode: str = "single",
    run_label: str | None = None,
) -> str:
    """Log a completed LLM call to Postgres + Confident AI. Returns trace_id."""
    trace_id = str(uuid.uuid4())

    # 1. Postgres (always)
    try:
        log_run(
            model_id=model_id,
            model_type=model_type,
            prompt=prompt,
            output=output,
            error=error,
            elapsed_sec=elapsed_sec,
            mode=mode,
            trace_id=trace_id,
        )
    except Exception as exc:
        print(f"[tracer] DB log failed: {exc}")

    # 2. Confident AI (if key is set)
    if _DEEPEVAL_OK:
        try:
            _send_to_confident(
                trace_id=trace_id,
                model_id=model_id,
                model_type=model_type,
                prompt=prompt,
                output=output or "",
                error=error,
                elapsed_sec=elapsed_sec,
                mode=mode,
                run_label=run_label,
            )
        except Exception as exc:
            print(f"[tracer] Confident AI send failed: {exc}")

    return trace_id


def _send_to_confident(
    *,
    trace_id: str,
    model_id: str,
    model_type: str,
    prompt: str,
    output: str,
    error: str | None,
    elapsed_sec: float,
    mode: str,
    run_label: str | None,
) -> None:
    tag = run_label or f"{model_type}:{mode}"

    # @observe captures the function arg as input and return value as output
    @observe(type="llm", model=model_id, name=f"{tag}:{model_id}")
    def _run(input: str) -> str:
        update_llm_span(model=model_id)
        return output if not error else f"ERROR: {error}"

    _run(prompt)
    try:
        trace_manager.post_trace()  # type: ignore[attr-defined]
    except Exception:
        pass
