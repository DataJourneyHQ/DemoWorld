"""
app.py — Streamlit UI for OSS vs Commercial LLM demo.
Supports single-model and side-by-side comparison modes.
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor

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

TYPE_OSS        = "🔓 Open Source"
TYPE_COMMERCIAL = "🏢 Commercial"

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OSS vs Commercial LLM",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 OSS vs Commercial LLM")
st.caption("DataJourneyHQ · Week 02 Demo — deploy proof-of-concept on Railway")
st.divider()


# ── helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_catalog(token: str) -> list[dict]:
    from evaluate.prompt_evaluator import fetch_catalog, score_model
    models = fetch_catalog(token)
    scored = sorted(
        [(score_model(m), m) for m in models],
        key=lambda x: x[0],
        reverse=True,
    )
    return [m for _, m in scored[:15]]


def call_model(model_id: str, is_oss: bool, prompt: str) -> tuple[str, str | None, float]:
    """Call one model. Returns (output, error, elapsed_seconds)."""
    try:
        api_key  = os.getenv("HF_TOKEN") if is_oss else os.getenv("GITHUB_TOKEN")
        base_url = HF_ENDPOINT           if is_oss else GITHUB_ENDPOINT
        model_arg = model_id if is_oss else model_id.split("/")[-1]

        if not api_key:
            token_name = "HF_TOKEN" if is_oss else "GITHUB_TOKEN"
            return "", f"`{token_name}` is not set.", 0.0

        client = OpenAI(base_url=base_url, api_key=api_key)
        t0 = time.perf_counter()
        response = client.chat.completions.create(
            model=model_arg,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
        )
        elapsed = time.perf_counter() - t0
        return response.choices[0].message.content, None, elapsed
    except Exception as exc:
        return "", str(exc), 0.0


def save_output(output: str, label: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = OUTPUT_DIR / f"{label}_output_{ts}.md"
    out_file.write_text(output, encoding="utf-8")
    return out_file


def model_selector(col_label: str, key_prefix: str, top_models: list[dict]) -> tuple[str | None, bool]:
    """Renders model-type radio + model picker. Returns (model_id, is_oss)."""
    model_type = st.radio(
        f"Model type",
        [TYPE_OSS, TYPE_COMMERCIAL],
        horizontal=True,
        key=f"{key_prefix}_type",
    )

    if model_type == TYPE_OSS:
        st.info(f"`{OSS_MODEL}`  \nHuggingFace Router", icon="🔓")
        return OSS_MODEL, True
    else:
        if not top_models:
            st.error("⚠️ `GITHUB_TOKEN` not set — cannot load catalog.")
            return None, False
        options   = [f"{m.get('name')}  ({m.get('id')})" for m in top_models]
        model_ids = [m.get("id") for m in top_models]
        idx = st.selectbox(
            "Pick a model",
            range(len(options)),
            format_func=lambda i: options[i],
            key=f"{key_prefix}_pick",
        )
        summary = top_models[idx].get("summary") or ""
        if summary:
            st.caption(f"📄 {summary[:120]}…" if len(summary) > 120 else f"📄 {summary}")
        return model_ids[idx], False


# ── pre-load catalog once ─────────────────────────────────────────────────────
gh_token   = os.getenv("GITHUB_TOKEN")
top_models = get_catalog(gh_token) if gh_token else []

# ── default prompt ────────────────────────────────────────────────────────────
default_prompt = (
    PROMPT_FILE.read_text(encoding="utf-8")
    if PROMPT_FILE.exists()
    else "Write a movie review of Project Hail Mary by Andy Weir."
)

# ── mode toggle ───────────────────────────────────────────────────────────────
mode = st.radio(
    "Mode",
    ["Single model", "Side-by-side comparison"],
    horizontal=True,
    label_visibility="collapsed",
)
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SINGLE MODEL MODE
# ══════════════════════════════════════════════════════════════════════════════
if mode == "Single model":
    st.subheader("① Select a model")
    model_id, is_oss = model_selector("Model", "single", top_models)

    st.divider()
    st.subheader("② Prompt")
    prompt_text = st.text_area(
        "Edit the prompt — default loaded from `prompt/prompt.md`",
        value=default_prompt,
        height=280,
        key="single_prompt",
    )

    st.divider()
    st.subheader("③ Generate")
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        run = st.button("🚀 Generate", type="primary",
                        disabled=not model_id, use_container_width=True)
    with col_info:
        if model_id:
            st.caption(f"Will run: `{model_id}`")

    if run:
        with st.spinner(f"Running `{model_id}` …"):
            output, err, elapsed = call_model(model_id, is_oss, prompt_text)
        if err:
            st.error(f"❌ {err}")
        else:
            label    = "oss" if is_oss else "commercial"
            out_file = save_output(output, label)
            st.success(f"✅ Saved to `{out_file.name}`  ·  ⏱ {elapsed:.2f}s")
            st.divider()
            with st.expander("📄 Output", expanded=True):
                st.markdown(output)
            st.download_button("⬇️ Download as Markdown", data=output,
                               file_name=out_file.name, mime="text/markdown")


# ══════════════════════════════════════════════════════════════════════════════
# SIDE-BY-SIDE COMPARISON MODE
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("① Select two models to compare")
    col_a, col_sep, col_b = st.columns([10, 1, 10])

    with col_a:
        st.markdown("#### Model A")
        model_a, is_oss_a = model_selector("Model A", "cmp_a", top_models)

    with col_sep:
        st.markdown(
            "<div style='border-left:1px solid #444;height:200px;margin:0 auto'></div>",
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown("#### Model B")
        model_b, is_oss_b = model_selector("Model B", "cmp_b", top_models)

    st.divider()
    st.subheader("② Prompt  *(shared)*")
    prompt_text = st.text_area(
        "Edit the prompt — default loaded from `prompt/prompt.md`",
        value=default_prompt,
        height=280,
        key="cmp_prompt",
    )

    st.divider()
    st.subheader("③ Run comparison")

    both_ready = bool(model_a and model_b)
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        run = st.button("⚡ Compare", type="primary",
                        disabled=not both_ready, use_container_width=True)
    with col_info:
        if both_ready:
            tag_a = "OSS" if is_oss_a else "Commercial"
            tag_b = "OSS" if is_oss_b else "Commercial"
            st.caption(
                f"A: `{model_a}` ({tag_a})   ·   B: `{model_b}` ({tag_b})"
            )

    if run:
        with st.spinner("Running both models in parallel …"):
            with ThreadPoolExecutor(max_workers=2) as pool:
                fut_a = pool.submit(call_model, model_a, is_oss_a, prompt_text)
                fut_b = pool.submit(call_model, model_b, is_oss_b, prompt_text)
                out_a, err_a, elapsed_a = fut_a.result()
                out_b, err_b, elapsed_b = fut_b.result()

        st.divider()
        res_a, res_b = st.columns(2)

        # ── Column A ──────────────────────────────────────────────────────────
        with res_a:
            tag_a   = "oss" if is_oss_a else "commercial"
            label_a = model_a.split("/")[-1]
            st.markdown(f"### A · `{label_a}`")
            if err_a:
                st.error(f"❌ {err_a}")
            else:
                file_a = save_output(out_a, f"A_{tag_a}_{label_a}")
                st.success(f"✅ Saved `{file_a.name}`  ·  ⏱ {elapsed_a:.2f}s")
                with st.expander("📄 Output A", expanded=True):
                    st.markdown(out_a)
                st.download_button(
                    "⬇️ Download A", data=out_a,
                    file_name=file_a.name, mime="text/markdown",
                    key="dl_a",
                )

        # ── Column B ──────────────────────────────────────────────────────────
        with res_b:
            tag_b   = "oss" if is_oss_b else "commercial"
            label_b = model_b.split("/")[-1]
            st.markdown(f"### B · `{label_b}`")
            if err_b:
                st.error(f"❌ {err_b}")
            else:
                file_b = save_output(out_b, f"B_{tag_b}_{label_b}")
                st.success(f"✅ Saved `{file_b.name}`  ·  ⏱ {elapsed_b:.2f}s")
                with st.expander("📄 Output B", expanded=True):
                    st.markdown(out_b)
                st.download_button(
                    "⬇️ Download B", data=out_b,
                    file_name=file_b.name, mime="text/markdown",
                    key="dl_b",
                )
