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

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env.example")

CATALOG_API  = "https://models.github.ai/catalog/models"
CATALOG_DIR  = ROOT / "pipeline_execute" / "catalog"

# ── prompt context ────────────────────────────────────────────────────────────
PROMPT_CONTEXT = {
    "task_type": "creative_writing",
    "needs": [
        "narrative", "character analysis", "tone",
        "science communication", "comparative analysis", "structured output",
    ],
}

# ── family preference: best for creative + nuanced writing first ──────────────
PREFERRED_FAMILIES = [
    "claude",    # Anthropic — best for creative + nuanced writing
    "gpt-4o",   # OpenAI GPT-4o family
    "gpt-4",    # fallback GPT-4
    "gemini",   # Google
    "mistral",  # Mistral large
]


# ── 1. Fetch catalog (same API call as the GitHub Action) ─────────────────────
def fetch_catalog(token: str) -> list[dict]:
    """Call the GitHub Models catalog endpoint — identical to the action's curl."""
    print("Fetching GitHub Models catalog...")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = requests.get(CATALOG_API, headers=headers, timeout=30)
    resp.raise_for_status()
    models = resp.json()
    print(f"Total models in catalog: {len(models)}")
    return models


# ── 2. Save catalog artifacts (mirrors the action's 3 artifact files) ─────────
def save_catalog_artifacts(models: list[dict]) -> None:
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)

    # github-models.json — full catalog
    (CATALOG_DIR / "github-models.json").write_text(json.dumps(models, indent=2))

    # github-models-mini.json — id / name / summary only
    mini = [{"id": m.get("id"), "name": m.get("name"), "summary": m.get("summary")} for m in models]
    (CATALOG_DIR / "github-models-mini.json").write_text(json.dumps(mini, indent=2))

    # models-report.md
    lines = [
        "# GitHub Models Catalog\n",
        f"Total models: {len(models)}\n\n",
        "Powered by DataJourneyHQ\nhttps://github.com/DataJourneyHQ\n\n",
    ]
    for m in models:
        lines.append(f"- **{m.get('name')}** (`{m.get('id')}`): {m.get('summary') or 'No summary'}\n")
    (CATALOG_DIR / "models-report.md").write_text("".join(lines))

    print(f"Catalog artifacts saved -> {CATALOG_DIR}")


# ── 3. Score each model against the prompt context ────────────────────────────
def score_model(model: dict) -> int:
    score    = 0
    combined = " ".join([
        model.get("id")      or "",
        model.get("name")    or "",
        model.get("summary") or "",
    ]).lower()

    for rank, family in enumerate(PREFERRED_FAMILIES):
        if family in combined:
            score += (len(PREFERRED_FAMILIES) - rank) * 10
            break

    for kw in ["creative", "writing", "reasoning", "nuanced", "instruction", "multilingual", "context", "long"]:
        if kw in combined:
            score += 3

    for p in ["embed", "vision", "mini", "nano", "small", "phi-3"]:
        if p in combined:
            score -= 8

    return score


def pick_best_model(models: list[dict]) -> dict:
    scored = sorted([(score_model(m), m) for m in models], key=lambda x: x[0], reverse=True)

    print("\nTop 5 candidates for this prompt:")
    for s, m in scored[:5]:
        print(f"  score={s:3d}  {m.get('id')}")

    return scored[0][1]


# ── 4. Full pipeline ──────────────────────────────────────────────────────────
def evaluate_and_pick() -> str:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN not set — needed to call the catalog API")

    models = fetch_catalog(token)
    save_catalog_artifacts(models)
    best   = pick_best_model(models)

    print(f"\nSelected model : {best.get('name')}")
    print(f"Model ID       : {best.get('id')}")
    print(f"Summary        : {best.get('summary')}\n")

    return best.get("id")


if __name__ == "__main__":
    model_id = evaluate_and_pick()
    print(f"-> Use this model in your commercial script: {model_id}")
