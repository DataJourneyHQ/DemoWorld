"""
tracer.py — unified logger: Postgres + Confident AI (deepeval).

Every LLM run is captured as:
  1. A row in `llm_runs` (source of truth for SQL queries)
  2. A trace in Confident AI (dashboard, evals, comparisons)

Both share the same `trace_id` so you can pivot between them.

Deepeval is OPTIONAL — if DEEPEVAL_API_KEY is missing or the SDK
is unavailable (pydantic conflict, etc.) we silently fall back to
DB-only logging. The app never breaks because of tracing.
"""
from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from typing import Any

from db import log_run

# ── optional deepeval import ─────────────────────────────────────────────────
_DEEPEVAL_OK = False
try:
    from deepeval.tracing import observe, update_current_span, trace_manager  # type: ignore
    from deepeval.tracing.attributes import LlmAttributes               # type: ignore
    _DEEPEVAL_OK = bool(os.getenv("CONFIDENT_API_KEY") or os.getenv("DEEPEVAL_API_KEY"))
    if _DEEPEVAL_OK and os.getenv("DEEPEVAL_API_KEY") and not os.getenv("CONFIDENT_API_KEY"):
        # deepeval reads CONFIDENT_API_KEY; honour either var name
        os.environ["CONFIDENT_API_KEY"] = os.environ["DEEPEVAL_API_KEY"]
except Exception as _exc:                                               # noqa: BLE001
    _DEEPEVAL_OK = False
    _import_err = _exc


def deepeval_enabled() -> bool:
    return _DEEPEVAL_OK


# ── main entry point ─────────────────────────────────────────────────────────
def log_llm_call(
    *,
    model_id: str,
    model_type: str,            # 'oss' | 'commercial'
    prompt: str,
    output: str | None,
    error: str | None,
    elapsed_sec: float,
    mode: str = "single",       # 'single' | 'comparison'
    prompt_tokens: int | None = None,
    output_tokens: int | None = None,
    run_label: str | None = None,
) -> str:
    """
    Log a single completed LLM call to Postgres AND Confident AI.
    Returns the shared trace_id so the caller can surface it in the UI.
    """
    trace_id = str(uuid.uuid4())

    # --- 1. Postgres (always) ------------------------------------------------
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
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
        )
    except Exception as exc:                                             # noqa: BLE001
        print(f"[tracer] DB log failed: {exc}")

    # --- 2. Confident AI (optional) -----------------------------------------
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
                prompt_tokens=prompt_tokens,
                output_tokens=output_tokens,
            )
        except Exception as exc:                                         # noqa: BLE001
            print(f"[tracer] Confident AI send failed: {exc}")

    return trace_id


# ── deepeval bridge ──────────────────────────────────────────────────────────
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
    prompt_tokens: int | None,
    output_tokens: int | None,
) -> None:
    """
    Emit one LLM span to Confident AI, tagged with our DB trace_id
    so a user can click a row in the DB and find the matching trace.
    """
    tag = run_label or f"{model_type}:{mode}"

    @observe(type="llm", model=model_id, name=f"{tag}:{model_id}")
    def _run() -> str:
        update_current_span(
            attributes=LlmAttributes(
                input=prompt,
                output=output if not error else f"ERROR: {error}",
                prompt_tokens=prompt_tokens or 0,
                completion_tokens=output_tokens or 0,
            ),
            metadata={
                "db_trace_id": trace_id,
                "model_type":  model_type,
                "mode":        mode,
                "elapsed_sec": round(elapsed_sec, 3),
                "error":       error or "",
            },
        )
        return output

    _run()
    # flush so the trace is visible immediately (Streamlit workers are short-lived)
    try:
        trace_manager.post_trace()                                       # type: ignore[attr-defined]
    except Exception:                                                    # noqa: BLE001
        pass
