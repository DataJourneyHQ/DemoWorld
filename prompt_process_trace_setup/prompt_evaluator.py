"""
prompt_evaluator.py

Mirrors what the DataJourneyHQ/list-github-models action does in CI —
but runs it locally in Python:

  curl -H "Authorization: Bearer $GH_TOKEN" \
       https://models.github.ai/catalog/models

Then evaluates the prompt context and picks the best available
commercial model for the task.
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CATALOG_API   = "https://models.github.ai/catalog/models"
CATALOG_DIR   = Path(__file__).parent / "catalog"
CATALOG_FILE  = CATALOG_DIR / "github-models.json"
MINI_FILE     = CATALOG_DIR / "github-models-mini.json"
REPORT_FILE   = CATALOG_DIR / "models-report.md"

# ── keywords that signal what the prompt needs ─────────────────────────────
PROMPT_CONTEXT = {
    "task_type": "creative_writing",
    "needs": [
        "narrative",
        "character analysis",
        "tone",
        "science communication",
        "comparative analysis",
        "structured output",
    ],
}

# ── preference order: families we consider "best" for creative + reasoning ─
PREFERRED_FAMILIES = [
    "claude",       # Anthropic — best for creative + nuanced writing
    "gpt-4o",       # OpenAI GPT-4o family
    "gpt-4",        # fallback GPT-4
    "gemini",       # Google
    "mistral",      # Mistral large
]


# ── 1. Fetch catalog (same logic as the GitHub Action) ─────────────────────

def fetch_catalog(token: str) -> list[dict]:
    """Call the GitHub Models catalog endpoint — identical to the action's curl."""
    print("📡  Fetching GitHub Models catalog …")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = requests.get(CATALOG_API, headers=headers, timeout=30)
    resp.raise_for_status()
    models = resp.json()
    print(f"✅  Total models in catalog: {len(models)}")
    return models


# ── 2. Save catalog artifacts (mirrors the action's artifact output) ────────

def save_catalog_artifacts(models: list[dict]) -> None:
    """Write the same three files the GitHub Action produces as artifacts."""
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)

    # github-models.json  — full catalog
    CATALOG_FILE.write_text(json.dumps(models, indent=2))

    # github-models-mini.json  — id / name / summary only
    mini = [{"id": m.get("id"), "name": m.get("name"), "summary": m.get("summary")} for m in models]
    MINI_FILE.write_text(json.dumps(mini, indent=2))

    # models-report.md
    lines = ["# GitHub Models Catalog\n", f"Total models: {len(models)}\n\n",
             "Powered by DataJourneyHQ 🚀\nhttps://github.com/DataJourneyHQ\n\n"]
    for m in models:
        lines.append(f"- **{m.get('name')}** (`{m.get('id')}`): {m.get('summary') or 'No summary'}\n")
    REPORT_FILE.write_text("".join(lines))

    print(f"💾  Catalog artifacts saved → {CATALOG_DIR}")


# ── 3. Evaluate prompt and score each model ─────────────────────────────────

def score_model(model: dict) -> int:
    """
    Score a model entry against the prompt context.
    Higher = better fit for creative writing + science communication.
    """
    score = 0
    model_id   = (model.get("id")   or "").lower()
    model_name = (model.get("name") or "").lower()
    summary    = (model.get("summary") or "").lower()
    combined   = f"{model_id} {model_name} {summary}"

    # family preference
    for rank, family in enumerate(PREFERRED_FAMILIES):
        if family in combined:
            score += (len(PREFERRED_FAMILIES) - rank) * 10
            break

    # capability keywords in summary
    creative_keywords = [
        "creative", "writing", "reasoning", "nuanced",
        "instruction", "multilingual", "context", "long"
    ]
    for kw in creative_keywords:
        if kw in summary:
            score += 3

    # penalise embed / vision-only / small models
    penalise = ["embed", "vision", "mini", "nano", "small", "phi-3"]
    for p in penalise:
        if p in combined:
            score -= 8

    return score


def pick_best_model(models: list[dict]) -> dict:
    """Return the highest-scoring model for our prompt context."""
    scored = [(score_model(m), m) for m in models]
    scored.sort(key=lambda x: x[0], reverse=True)

    print("\n🏆  Top 5 candidates for this prompt:")
    for s, m in scored[:5]:
        print(f"   score={s:3d}  {m.get('id')}")

    best_score, best = scored[0]
    return best


# ── 4. Main ─────────────────────────────────────────────────────────────────

def evaluate_and_pick() -> str:
    """
    Full pipeline:
      1. Fetch catalog (= what the GitHub Action does in CI)
      2. Save artifacts to catalog/
      3. Score every model against the prompt context
      4. Return the winning model id
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN not set — needed to call the catalog API")

    models  = fetch_catalog(token)
    save_catalog_artifacts(models)
    best    = pick_best_model(models)

    print(f"\n✨  Selected model  : {best.get('name')}")
    print(f"   Model ID        : {best.get('id')}")
    print(f"   Summary         : {best.get('summary')}\n")

    return best.get("id")


if __name__ == "__main__":
    model_id = evaluate_and_pick()
    print(f"→  Use this model in your commercial script: {model_id}")
