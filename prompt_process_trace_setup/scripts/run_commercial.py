"""
run_commercial.py
Commercial model runner — GitHub Models endpoint (Azure inference).
Step 1: calls evaluate_and_pick() — mirrors DataJourneyHQ/list-github-models
        action to fetch live catalog and score models against prompt context.
Step 2: runs winning model via GitHub Models inference endpoint.
Tracing: analytics_framework/evalute_llm/trace_setup_github_models.py
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from openai import OpenAI
from deepeval.tracing import observe
from dotenv import load_dotenv
from evaluate.prompt_evaluator import evaluate_and_pick

load_dotenv(ROOT / ".env.example")

GITHUB_ENDPOINT = "https://models.inference.ai.azure.com"

PROMPT_FILE = ROOT / "prompt" / "prompt.md"
OUTPUT_FILE = ROOT / "pipeline_execute" / "commercial_output.md"


def read_prompt() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8")


@observe()
def run_commercial_model(prompt: str, model_id: str) -> str:
    client = OpenAI(
        base_url=GITHUB_ENDPOINT,
        api_key=os.getenv("GITHUB_TOKEN"),
    )
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a sharp, witty film critic who loves hard sci-fi. "
                    "You write reviews that are both intellectually rigorous and emotionally resonant."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("Step 1 — evaluating prompt + fetching live GitHub Models catalog...")
    print("=" * 60)
    model_id = evaluate_and_pick()

    print(f"Step 2 — running commercial model: {model_id}")
    print(f"Endpoint: {GITHUB_ENDPOINT}")
    print("-" * 60)
    prompt = read_prompt()

    try:
        output = run_commercial_model(prompt, model_id)
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(output, encoding="utf-8")
        print(output)
        print("-" * 60)
        print(f"Output saved -> {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error: {e}")
