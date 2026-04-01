# Exciting Demos

<img width="878" height="786" alt="Screenshot 2026-03-19 at 12 59 31 PM" src="https://github.com/user-attachments/assets/efa7b04e-dce2-43c4-97dd-c269ff269d94" />


### 25th March CrewAI Demos 

1. OSS Discovery + Deployed via GitHub Action @sayantikabanik
2. API-first asset librarian for local-first document and image similarity analysis. https://github.com/arcnem-ai/omnivec @Kthom1
---

## GitHub Actions — CrewAI OSS Discovery Agent

A `workflow_dispatch` workflow that runs the CrewAI agent on demand directly from GitHub Actions. No local setup, no OpenAI account — just a GitHub PAT.

**How it works:**
1. You trigger it manually from the Actions tab with 3 inputs: `criteria`, `programming_languages`, `project_types`
2. The agent uses `gpt-4o-mini` routed through GitHub's model endpoint (`https://models.inference.ai.azure.com`) — authenticated via your GitHub token
3. It searches the web for open source projects, scrapes repos, and writes a discovery report
4. The report is saved as both `.md` and `.html` and uploaded as a downloadable artifact

**Only 1 secret needed:**
| Secret | What it is |
|---|---|
| `GH_MODELS_TOKEN` | Your GitHub PAT with Models read permission |

---

## ⚠️ Hallucination Risk — This Workflow Has a Known Issue

The workflow currently **completes successfully even when the search tool fails.**

Here's what actually happens at runtime:

```
Agent calls SerperDevTool to search the web
        │
        ▼ ❌ 403 Forbidden — SERPER_API_KEY missing or invalid
        │
        │  ERROR: 403 Client Error: Forbidden
        │  Tool: search_the_internet_with_serper
        │  Iteration: 26 — all 25 retries exhausted
        │
        ▼
Agent falls back to LLM training knowledge
        │
        ▼ ✅ GitHub Actions reports SUCCESS
Artifact uploaded — looks like a normal report
```

### Why this is a risk

The output **looks completely valid** — proper markdown, real project names, GitHub URLs, star counts. But it is generated entirely from the LLM's training data (knowledge cutoff: early 2024), not from live web search. There are no guardrails in place to detect or reject this.

| Risk | Detail |
|---|---|
| **Stale data** | Projects may be archived, renamed, or no longer maintained |
| **Fabricated URLs** | Links may point to wrong or non-existent repos |
| **False confidence** | Report reads as authoritative with no warning it failed |
| **CI shows green** | Nothing in the pipeline signals that tools broke |


---

### 1st april <> OSS vs Commercial LLM Evaluation
<img width="2572" height="500" alt="Screenshot 2026-04-01 at 9 39 30 AM" src="https://github.com/user-attachments/assets/6d716417-a3cb-4d8e-8250-a36f1f698bd9" />



A side-by-side comparison of an **open source model** (`gpt-oss-120b` via HuggingFace router) vs a **commercial GitHub Model** (selected dynamically from the live catalog) on a creative + science-heavy prompt — a movie review of *Project Hail Mary* by Andy Weir.

#### What it does

| Step | What happens |
|------|-------------|
| **1. Prompt** | Structured movie review task in `prompt/prompt.md` — narrative writing, character analysis, science accuracy, comparative reasoning |
| **2. Evaluate** | `evaluate/prompt_evaluator.py` calls the [DataJourneyHQ/list-github-models](https://github.com/DataJourneyHQ/list-github-models) action API (`https://models.github.ai/catalog/models`), fetches the live catalog, scores every model against the prompt context and picks the best commercial model |
| **3. OSS run** | `scripts/run_oss.py` — runs `openai/gpt-oss-120b:novita` via HuggingFace router with |
| **4. Commercial run** | `scripts/run_commercial.py` — calls the evaluator first, then runs the winning GitHub Model via `https://models.inference.ai.azure.com`|
| **5. Trace** TODO | `pipeline_execute/trace_setup.py` — configures [deepeval](https://github.com/confident-ai/deepeval) tracing so both runs are captured side-by-side in the Confident AI dashboard |

#### References
- [DataJourneyHQ/list-github-models](https://github.com/DataJourneyHQ/list-github-models) — GitHub Action that fetches the live models catalog
- [DataJourney analytics_framework](https://github.com/DataJourneyHQ/DataJourney/tree/main/analytics_framework) — trace setup + OSS prompt enhancer patterns used as base

#### Directory structure

```
prompt_process_trace_setup/
├── __init__.py
├── .env.example                    ← GITHUB_TOKEN, HF_TOKEN, DEEPEVAL_API_KEY
├── requirements.txt
│
├── prompt/
│   └── prompt.md                   ← movie review prompt (Project Hail Mary)
│
├── evaluate/
│   └── prompt_evaluator.py         ← fetches live GitHub Models catalog,
│                                      scores models, picks best commercial one
├── scripts/
│   ├── run_oss.py                  ← gpt-oss-120b via HuggingFace router
│   └── run_commercial.py           ← dynamically picked GitHub Model
│
└── pipeline_execute/
    └── trace_setup.py              ← deepeval @observe tracing config
```

#### How to run

```bash
cd prompt_process_trace_setup

# 1. install dependencies
pip install -r requirements.txt

# 2. copy and fill in your tokens
cp .env.example .env

# 3. run OSS model
python scripts/run_oss.py

# 4. run commercial model (evaluator picks the model automatically)
python scripts/run_commercial.py
```

> Outputs are saved to `pipeline_execute/oss_output.md` and `pipeline_execute/commercial_output.md`
