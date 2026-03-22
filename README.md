# Exciting Demos

### 25th March CrewAI

<img width="2878" height="1786" alt="Screenshot 2026-03-19 at 12 59 31 PM" src="https://github.com/user-attachments/assets/efa7b04e-dce2-43c4-97dd-c269ff269d94" />

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

