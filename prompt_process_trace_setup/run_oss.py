"""
run_oss.py

OSS model runner — openai/gpt-oss-120b via HuggingFace router.
Pattern mirrors: analytics_framework/gpt_oss/prompt_enhancer_oss_gpt_120b.py
Tracing via deepeval @observe() — mirrors: analytics_framework/evalute_llm/trace_setup_github_models.py
"""

import os
from pathlib import Path
from openai import OpenAI
from deepeval.tracing import observe
from dotenv import load_dotenv

load_dotenv()

# ── model config ────────────────────────────────────────────────────────────
MODEL_NAME = "openai/gpt-oss-120b:novita"
HF_ENDPOINT = "https://router.huggingface.co/v1"

# ── load prompt from prompt.md ───────────────────────────────────────────────
PROMPT_FILE = Path(__file__).parent / "prompt.md"
OUTPUT_FILE = Path(__file__).parent / "outputs" / "oss_output.md"


def read_prompt() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8")


# ── traced LLM call ──────────────────────────────────────────────────────────
@observe()
def run_oss_model(prompt: str) -> str:
    client = OpenAI(
        base_url=HF_ENDPOINT,
        api_key=os.getenv("HF_TOKEN"),
    )
    response = client.chat.completions.create(
        model=MODEL_NAME,
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


# ── main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🤖  Model   : {MODEL_NAME}")
    print(f"🔗  Endpoint: {HF_ENDPOINT}")
    print("─" * 60)

    prompt = read_prompt()

    try:
        output = run_oss_model(prompt)

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(output, encoding="utf-8")

        print(output)
        print("─" * 60)
        print(f"💾  Output saved → {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌  Error: {e}")
