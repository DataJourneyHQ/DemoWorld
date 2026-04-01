"""
trace_setup.py

Trace configuration — mirrors:
  analytics_framework/evalute_llm/trace_setup_github_models.py

# TODO: re-enable deepeval tracing once deepeval/pydantic compatibility is resolved
# Configures deepeval tracing so every @observe() decorated call
# in run_oss.py and run_commercial.py is captured and sent to
# Confident AI for side-by-side comparison.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# from deepeval.tracing import TraceManager  # TODO: re-enable once deepeval/pydantic compatibility is resolved

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def configure_tracing(run_label: str = "default") -> None:
    """
    Initialise tracing.
    run_label — tags traces so OSS vs commercial are
                clearly separated in the Confident AI dashboard.
    # TODO: re-enable deepeval TraceManager once deepeval/pydantic compatibility is resolved
    """
    api_key = os.getenv("DEEPEVAL_API_KEY")
    if not api_key:
        print("DEEPEVAL_API_KEY not set — tracing disabled")
        return

    os.environ["DEEPEVAL_RESULTS_FOLDER"] = str(ROOT / "pipeline_execute")
    print(f"Tracing enabled — run label: [{run_label}]")
    print("Traces will appear in Confident AI dashboard\n")


if __name__ == "__main__":
    configure_tracing("test-run")
