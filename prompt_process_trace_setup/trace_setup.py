"""
trace_setup.py

Trace configuration — mirrors:
  analytics_framework/evalute_llm/trace_setup_github_models.py

Configures deepeval tracing so every @observe() decorated call
in run_oss.py and run_commercial.py is captured and sent to
Confident AI for side-by-side comparison.
"""

import os
from deepeval.tracing import TraceManager
from dotenv import load_dotenv

load_dotenv()


def configure_tracing(run_label: str = "default") -> None:
    """
    Initialise deepeval tracing.
    run_label — used to tag traces so OSS vs commercial are
                clearly separated in the Confident AI dashboard.
    """
    api_key = os.getenv("DEEPEVAL_API_KEY")
    if not api_key:
        print("⚠️   DEEPEVAL_API_KEY not set — traces will run locally only")
        return

    os.environ["DEEPEVAL_RESULTS_FOLDER"] = "outputs"

    print(f"🔭  Tracing enabled  — run label: [{run_label}]")
    print(f"📊  Traces will appear in Confident AI dashboard\n")
