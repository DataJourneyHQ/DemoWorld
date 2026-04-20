"""
tracer.py — log LLM calls to Postgres + Confident AI.
"""
from __future__ import annotations
import os
import uuid
from deepeval.tracing import observe, update_llm_span, trace_manager
from db import log_run

trace_manager.configure(confident_api_key=os.getenv("CONFIDENT_API_KEY"))


def log_llm_call(
    *,
    model_id: str,
    model_type: str,
    prompt: str,
    output: str | None,
    error: str | None,
    elapsed_sec: float,
    mode: str = "single",
) -> str:
    trace_id = str(uuid.uuid4())

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

    @observe(type="llm", model=model_id, name=f"{model_type}:{mode}:{model_id}")
    def _send(input: str) -> str:
        update_llm_span(model=model_id)
        return output or ""

    _send(prompt)
    trace_manager.flush_traces()

    return trace_id
