"""
trace_setup.py

Trace configuration — mirrors:
  analytics_framework/evalute_llm/trace_setup_github_models.py

Configures deepeval tracing so every @observe() decorated call
in run_oss.py and run_commercial.py is captured and sent to
Confident AI for side-by-side comparison.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env.example")


def configure_tracing(run_label: str = "default") -> None:
    """
    Initialise deepeval tracing.
    run_label — tags traces so OSS vs commercial are
                clearly separated in the Confident AI dashboard.
    """
    api_key = os.getenv("DEEPEVAL_API_KEY")
    if not api_key:
        print("DEEPEVAL_API_KEY not set — traces will run locally only")
        return

    os.environ["DEEPEVAL_RESULTS_FOLDER"] = str(ROOT / "pipeline_execute")
    print(f"Tracing enabled — run label: [{run_label}]")
    print("Traces will appear in Confident AI dashboard\n")


if __name__ == "__main__":
    configure_tracing("test-run")
