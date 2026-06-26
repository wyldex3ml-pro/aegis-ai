# AegisAI — Autonomous Enterprise Incident Commander

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green)
![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.3-orange)
![Qdrant](https://img.shields.io/badge/VectorDB-Qdrant-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

AegisAI is a production-grade, open-source **Multi-Agent System** that autonomously detects software errors, diagnoses them using RAG (Retrieval-Augmented Generation), and automatically generates and tests code fixes — all without human intervention.

---

## 🎥 Demo

```
🔍 Triage Agent    → Fetches similar past incidents from Qdrant vector DB
💻 Coder Agent     → Calls Groq LLaMA 3.3 70B to generate a Python fix
🧪 Tester Agent    → Executes the patch in a secure sandbox
🔁 Self-Healing    → Retries up to 3 times if the fix fails
✅ Auto-Resolved   → Status: FIXED in 2 seconds, 0 retries
```

---

## 🏗️ Architecture

```
Incoming Error
      │
      ▼
┌─────────────┐     ┌─────────────────┐
│ Triage Agent│────▶│ Qdrant VectorDB │
│             │◀────│ (RAG Context)   │
└──────┬──────┘     └─────────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────────┐
│ Coder Agent │────▶│ Groq LLaMA 3.3  │
│             │◀────│ (Code Fix)      │
└──────┬──────┘     └─────────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────────┐
│ Tester Agent│────▶│ Local Sandbox   │
│             │◀────│ (subprocess)    │
└──────┬──────┘     └─────────────────┘
       │
       ▼
  ┌────┴────┐
  │ Router  │──── PASS ──▶ ✅ FIXED
  │         │──── FAIL ──▶ 🔁 Retry (max 3)
  └─────────┘──── MAX  ──▶ ❌ Escalate
```

---

## 🧰 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent Orchestration | LangGraph | Stateful multi-agent workflow |
| LLM | Groq Llama 3.3 70B | Code fix generation |
| Vector Database | Qdrant (in-memory) | RAG — historical incident memory |
| Code Execution | Python subprocess | Secure sandboxed patch testing |
| State Management | TypedDict + operator.add | Shared agent memory with audit trail |
| Config | python-dotenv | Secure API key management |

---

## 📁 Project Structure

```
aegis-ai/
├── state.py          # Shared state schema (TypedDict) — agent memory blueprint
├── rag_storage.py    # Qdrant vector DB — stores and retrieves past incidents
├── nodes.py          # Three agent nodes: Triage, Coder, Tester
├── main.py           # LangGraph assembly — self-healing retry loop
├── .env              # API keys (never committed)
└── .gitignore        # Protects secrets and ignores build artifacts
```

---

## ⚙️ How It Works

### 1. State (`state.py`)
A `TypedDict` acts as the shared memory between all agents. Every agent reads from it and writes to it. Fields include `error_log`, `historical_context`, `current_patch`, `test_results`, `retry_count`, and an append-only `patch_history` for full audit trails.

### 2. RAG Memory (`rag_storage.py`)
Uses Qdrant's in-memory vector database to store past incidents as embeddings. When a new error arrives, it retrieves the most similar past incidents and their successful fixes, giving the Coder Agent relevant historical context instead of guessing blind.

### 3. Agent Nodes (`nodes.py`)
- **Triage Agent** — queries the RAG database for similar past incidents
- **Coder Agent** — calls the LLM with the error + RAG context to generate a fix
- **Tester Agent** — runs the fix in a sandboxed subprocess and records the result

### 4. Graph (`main.py`)
LangGraph wires the agents into a directed graph with a conditional router after the Tester Agent. If the patch passes, the graph ends with `status: fixed`. If it fails, the graph loops back to the Coder Agent with the failed attempt in context. After 3 retries, it escalates.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- A free [Groq API key](https://console.groq.com)

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/aegis-ai.git
cd aegis-ai

# Create virtual environment
python -m venv .venv

# Activate (Mac/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install langgraph langchain-core qdrant-client python-dotenv langchain-openai groq
```

### Configuration

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Run

```bash
python main.py
```

---

## 📊 Example Output

```
🔍 Triage Agent started.
   RAG context retrieved — 2 similar incidents found.

💻 Coder Agent started. Retry #0
   Patch generated (699 chars).

🧪 Tester Agent started.
   Sandbox result: EXIT_CODE: 0 | Total: 30.0

✅ INCIDENT RESOLVED AUTOMATICALLY
   Status       : FIXED
   Retries used : 0 / 3
   Patches tried: 1
```

---

## 🔮 Roadmap

- [ ] Real semantic embeddings via `sentence-transformers`
- [ ] GitHub webhook integration for automatic error ingestion
- [ ] Slack/PagerDuty alerting on escalation
- [ ] Web dashboard for incident history
- [ ] E2B cloud sandbox integration
- [ ] Support for JavaScript / TypeScript codebases

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Author

Built as a portfolio project demonstrating production-grade Multi-Agent System design using LangGraph, RAG, and autonomous code repair.