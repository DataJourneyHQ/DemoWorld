"""
app.py — Streamlit UI for OSS vs Commercial LLM demo.
Runs locally and deploys on Railway.
"""
import os
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

# ── constants ─────────────────────────────────────────────────────────────────
OSS_MODEL       = "openai/gpt-oss-120b:novita"
HF_ENDPOINT     = "https://router.huggingface.co/v1"
GITHUB_ENDPOINT = "https://models.inference.ai.azure.com"
PROMPT_FILE     = ROOT / "prompt" / "prompt.md"
OUTPUT_DIR      = ROOT / "pipeline_execute"

SYSTEM_PROMPT = (
    "You are a sharp, witty film critic who loves hard sci-fi. "
    "You write reviews that are both intellectually rigorous and emotionally resonant."
)

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OSS vs Commercial LLM",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 OSS vs Commercial LLM")
st.caption("DataJourneyHQ · Week 02 Demo — deploy proof-of-concept on Railway")
st.divider()


# ── 1. catalog fetch (cached so it only hits the API once per session) ────────
@st.cache_data(show_spinner=False)
def get_catalog(token: str) -> list[dict]:
    from evaluate.prompt_evaluator import fetch_catalog, score_model
    models = fetch_catalog(token)
    scored = sorted(
        [(score_model(m), m) for m in models],
        key=lambda x: x[0],
        reverse=True,
    )
    return [m for _, m in scored[:15]]   # top 15 candidates


# ── 2. model selection ────────────────────────────────────────────────────────
st.subheader("① Select a model")

model_type = st.radio(
    "Model type",
    ["🔓 Open Source", "🏢 Commercial (GitHub Models)"],
    horizontal=True,
)

selected_model_id: str | None = None

if model_type == "🔓 Open Source":
    st.info(
        f"**Fixed model:** `{OSS_MODEL}`  \n"
        "Routed via HuggingFace · requires `HF_TOKEN`"
    )
    selected_model_id = OSS_MODEL

else:
    gh_token = os.getenv("GITHUB_TOKEN")
    if not gh_token:
        st.error("⚠️ `GITHUB_TOKEN` is not set — add it to your `.env` or Railway env vars.")
    else:
        with st.spinner("Fetching live GitHub Models catalog…"):
            top_models = get_catalog(gh_token)

        options      = [f"{m.get('name')}  —  `{m.get('id')}`" for m in top_models]
        model_ids    = [m.get("id") for m in top_models]
        summaries    = [m.get("summary") or "" for m in top_models]

        chosen_idx = st.selectbox(
            "Choose a commercial model (ranked by fit for this prompt)",
            range(len(options)),
            format_func=lambda i: options[i],
        )
        selected_model_id = model_ids[chosen_idx]
        if summaries[chosen_idx]:
            st.caption(f"📄 {summaries[chosen_idx]}")

st.divider()


# ── 3. prompt editor ──────────────────────────────────────────────────────────
st.subheader("② Prompt")

default_prompt = (
    PROMPT_FILE.read_text(encoding="utf-8")
    if PROMPT_FILE.exists()
    else "Write a movie review of Project Hail Mary by Andy Weir."
)

prompt_text = st.text_area(
    "Edit the prompt — default loaded from `prompt/prompt.md`",
    value=default_prompt,
    height=320,
)

st.divider()


# ── 4. generate ───────────────────────────────────────────────────────────────
st.subheader("③ Generate")

col_btn, col_info = st.columns([1, 3])
with col_btn:
    run = st.button(
        "🚀 Generate",
        type="primary",
        disabled=(selected_model_id is None),
        use_container_width=True,
    )
with col_info:
    if selected_model_id:
        st.caption(f"Will run: `{selected_model_id}`")

if run:
    is_oss = model_type == "🔓 Open Source"

    api_key  = os.getenv("HF_TOKEN") if is_oss else os.getenv("GITHUB_TOKEN")
    base_url = HF_ENDPOINT           if is_oss else GITHUB_ENDPOINT

    # GitHub Models strips the "openai/" provider prefix
    model_arg = selected_model_id if is_oss else selected_model_id.split("/")[-1]

    if not api_key:
        token_name = "HF_TOKEN" if is_oss else "GITHUB_TOKEN"
        st.error(f"⚠️ `{token_name}` is not set.")
    else:
        with st.spinner(f"Running `{selected_model_id}` …  this may take ~30 s"):
            try:
                client = OpenAI(base_url=base_url, api_key=api_key)
                response = client.chat.completions.create(
                    model=model_arg,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": prompt_text},
                    ],
                )
                output = response.choices[0].message.content

                # save ──────────────────────────────────────────────────────
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
                label     = "oss" if is_oss else "commercial"
                out_file  = OUTPUT_DIR / f"{label}_output_{ts}.md"
                out_file.write_text(output, encoding="utf-8")

                # display ───────────────────────────────────────────────────
                st.success(f"✅ Done · saved to `{out_file.name}`")
                st.divider()

                with st.expander("📄 Output", expanded=True):
                    st.markdown(output)

                st.download_button(
                    label="⬇️ Download as Markdown",
                    data=output,
                    file_name=out_file.name,
                    mime="text/markdown",
                )

            except Exception as exc:
                st.error(f"❌ Error: {exc}")
