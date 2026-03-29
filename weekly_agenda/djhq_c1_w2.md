## 📅 Week 02 Live Session Agenda
**Date:** 1 April 2026
**Theme:** From ideas to code, making your first real API calls and choosing the right model for the job

---

### Recap from Week 01

We will open with a quick look back at what we covered last week and give everyone a chance to share how their v0 workflow sketch is coming along. This is also a good moment to surface anything that felt unclear or did not quite land.

| | |
|---|---|
| 🗣️ | Open floor: what clicked and what felt confusing from Week 01 |
| 🏗️ | Share your workflow sketches, even if they are rough, that is the point |
| 🐛 | What is working, what is not — let us troubleshoot together |

---

### What We Will Cover

| | Topic |
|---|---|
| 🔑 | **API key setup via Bitwarden** — your keys have been sent securely. Check your email for instructions on how to retrieve them from the shared Bitwarden vault |
| 🐍 | Setting up a clean Python project from scratch — folder structure, virtual environments and keeping things organised |
| 📝 | Writing your first scripts and how to think about a script as a single focused unit of work |
| 🌐 | Making API calls in GitHub Actions and turning a local script into something that runs in CI |
| 🔍 | Reading API responses and understanding what the data actually looks like |
| 🧪 | What happens when things go wrong — error handling and how to debug API calls |
| ☕ | Office hours for any questions, blockers or anything you need clarity on |

---

### Open Source vs Commercial LLMs

One of the most important decisions you will make in any AI project is which model to use. We will walk through this together so you can make informed choices rather than just defaulting to the most popular option.

| | |
|---|---|
| 🏢 | **Commercial models** — OpenAI GPT-4o, Anthropic Claude, GitHub Copilot models. Managed infrastructure, strong out of the box performance, usage based cost |
| 🔓 | **Open source models** — Mistral, LLaMA 3, Phi-3, Gemma. Self hosted or via providers like Ollama, Groq and Together AI. More control, lower cost at scale |
| 💰 | **Cost comparison** — a side by side breakdown of what different models actually cost per million tokens so you can size this against your project needs |

#### Cost Comparison at a Glance

| Model | Type | Input per 1M tokens | Output per 1M tokens |
|---|---|---|---|
| GPT-4o | Commercial | ~$5.00 | ~$15.00 |
| GPT-4o mini | Commercial | ~$0.15 | ~$0.60 |
| Claude 3.5 Haiku | Commercial | ~$0.80 | ~$4.00 |
| GitHub Models (gpt-4o-mini) | Commercial | Free tier via PAT | Free tier via PAT |
| Groq (LLaMA 3 70B) | Open source hosted | ~$0.59 | ~$0.79 |
| Mistral 7B (self hosted) | Open source | Infrastructure cost only | Infrastructure cost only |

> Prices are approximate and change frequently. Always check the provider pricing page before committing to a model for production use.

---

### Guest Demo — Building UI Experiences with LLMs

**Presented by Rey**

Rey will walk us through how to build real user facing experiences powered by LLMs. This is not just about API calls in a terminal — it is about what happens when you put an LLM in front of an actual user.

| | |
|---|---|
| 🎨 | How to think about UI design when the output is generative and unpredictable |
| ⚡ | Streaming responses so the interface feels fast and responsive |
| 🧩 | Structuring LLM output so it is renderable and useful in a UI context |
| 🛠️ | A live build — watch Rey put something together from scratch |

---

### Before the Session

Please make sure you have done the following before we start:

1. Check your email for the Bitwarden invitation and follow the instructions to access your API key
2. Confirm Python is installed by running `python --version` in your terminal
3. Bring your v0 workflow sketch — even a rough notes doc counts!

---

### Goal for Week 02

By the end of this session you should feel confident **setting up a Python project, understanding your model options and their costs, making a real API call and seeing how LLMs can power a UI experience**. The goal is to leave with enough context to start making real technical decisions for your own project.
