<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:060E1F,50:1F4E79,100:2E75B6&height=200&section=header&text=AEGIS%20AI&fontSize=72&fontColor=ffffff&fontAlignY=35&desc=Autonomous%20Enterprise%20Incident%20Commander&descAlignY=55&descSize=22&descColor=7EB8E8" width="100%"/>

<br/>

[![Live API](https://img.shields.io/badge/🚀%20LIVE%20API-Click%20Here-2E75B6?style=for-the-badge&logoColor=white)](https://aegis-ai-cr2u.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-1F4E79?style=for-the-badge&logo=github)](https://github.com/wyldex3ml-pro/aegis-ai)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6B35?style=for-the-badge&logoColor=white)](https://langchain.com)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)

<br/>

> **🔥 An autonomous AI system that detects, triages, and resolves enterprise incidents using coordinated multi-agent architecture — no human intervention required for Level-1 incidents.**

<br/>

---

</div>

## 🎯 What Problem Does This Solve?

Enterprise incidents — system outages, security breaches, performance failures — cost companies millions every hour they go unresolved. Traditional incident management requires:

- On-call engineers available 24/7
- Manual triage of every alert
- Slow escalation chains
- Knowledge locked in documentation no one can find fast enough

**Aegis AI eliminates all of this.**

```
WITHOUT Aegis AI:                 WITH Aegis AI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Engineer woken at 3AM          ✅ AI handles it autonomously
❌ Manual triage — 20 minutes     ✅ Triage in seconds
❌ Digging through docs           ✅ RAG finds the answer instantly
❌ Slow escalation chain          ✅ Instant intelligent routing
❌ Repeated same incidents        ✅ AI learns from every incident
```

---

## 🚀 Live Demo

**👉 [https://aegis-ai-cr2u.onrender.com](https://aegis-ai-cr2u.onrender.com)**

> Fully deployed production API — accessible from anywhere in the world.

---

## ⚡ Key Features

```
🤖  Multi-Agent Architecture    →  Coordinated AI agents handle detection to resolution
🧠  RAG Knowledge Base          →  Retrieves relevant docs instantly using vector search
📊  State Management            →  Tracks full incident lifecycle with LangGraph state
🔍  Intelligent Triage          →  Classifies severity, category, and priority automatically
⚡  Autonomous Resolution       →  Resolves Level-1 incidents without human input
📡  REST API                    →  Clean API for integration with any monitoring system
🌐  Web Interface               →  Built-in dashboard via templates
```

---

## 🏗️ Multi-Agent Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          AEGIS AI SYSTEM                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   🚨 Incident Detected                                                │
│         │                                                             │
│         ▼                                                             │
│   ┌─────────────────┐                                                 │
│   │   STATE MANAGER │  ◀── state.py                                   │
│   │   (LangGraph)   │      Tracks full incident context               │
│   └────────┬────────┘                                                 │
│            │                                                          │
│    ┌───────┼───────┐                                                  │
│    ▼       ▼       ▼                                                  │
│ ┌──────┐ ┌──────┐ ┌──────────────┐                                    │
│ │Triage│ │  RAG │ │  Resolution  │  ◀── nodes.py                      │
│ │Agent │ │Agent │ │    Agent     │      LangGraph nodes                │
│ └──┬───┘ └──┬───┘ └──────┬───────┘                                    │
│    │        │             │                                            │
│    │    ┌───▼────────┐    │                                            │
│    │    │RAG STORAGE │    │  ◀── rag_storage.py                        │
│    │    │Vector DB   │    │      Knowledge base retrieval              │
│    │    └────────────┘    │                                            │
│    │                      │                                            │
│    └──────────┬───────────┘                                            │
│               ▼                                                        │
│   ┌───────────────────────┐                                            │
│   │    RESOLUTION OUTPUT  │                                            │
│   │  + Escalation if      │                                            │
│   │    Level-2 needed     │                                            │
│   └───────────────────────┘                                            │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Core Components

| File | Purpose |
|---|---|
| `app.py` | Main application — API endpoints and web server |
| `main.py` | Entry point — initialises and runs the agent system |
| `nodes.py` | LangGraph nodes — individual AI agent logic |
| `rag_storage.py` | RAG pipeline — vector storage and knowledge retrieval |
| `state.py` | LangGraph state — incident context and lifecycle tracking |
| `templates/index.html` | Web dashboard UI |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Agent Framework** | LangGraph | Multi-agent workflow orchestration |
| **AI Model** | LLaMA 3.3 70B via Groq | Agent reasoning and decision making |
| **RAG Pipeline** | FAISS + Embeddings | Knowledge base vector search |
| **State Management** | LangGraph State | Incident lifecycle tracking |
| **Web Framework** | FastAPI / Flask | REST API and web interface |
| **Deployment** | Render | Live cloud hosting |
| **Language** | Python 3.11 | Core application |

---

## 🧠 LangGraph Agent Workflow

```python
# Simplified agent flow in nodes.py

def triage_agent(state: IncidentState) -> IncidentState:
    """Classifies incident severity, category and priority"""
    ...

def rag_agent(state: IncidentState) -> IncidentState:
    """Retrieves relevant knowledge from vector database"""
    ...

def resolution_agent(state: IncidentState) -> IncidentState:
    """Generates resolution steps or escalates if needed"""
    ...

# LangGraph orchestrates the full pipeline
workflow = StateGraph(IncidentState)
workflow.add_node("triage", triage_agent)
workflow.add_node("rag_lookup", rag_agent)
workflow.add_node("resolve", resolution_agent)
```

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.11+
Groq API Key (free at console.groq.com)
```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/wyldex3ml-pro/aegis-ai.git
cd aegis-ai

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Run the Application

```bash
python main.py
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web dashboard |
| `POST` | `/incident` | Submit new incident for AI processing |
| `GET` | `/status/{id}` | Get incident resolution status |

### Example Request

```json
POST /incident
{
  "title": "Database connection timeout",
  "severity": "high",
  "description": "Production DB connections failing since 14:32 UTC"
}
```

### Example Response

```json
{
  "incident_id": "INC-2026-001",
  "severity": "high",
  "category": "database",
  "triage_result": "Connection pool exhaustion detected",
  "knowledge_retrieved": "Run: SELECT count(*) FROM pg_stat_activity",
  "resolution": "Restart connection pool service — estimated fix: 3 minutes",
  "escalate": false
}
```

---

## 🎯 Real World Business Impact

```
⏱️  Triage time:               20 minutes → Seconds
🌙  On-call interruptions:     Eliminated for Level-1 incidents
📚  Knowledge retrieval:       Instant via RAG vector search
💰  Cost per incident:         Dramatically reduced
🔄  Repeat incidents:          Reduced through AI pattern recognition
```

---

## 🔮 Future Roadmap

- [ ] PagerDuty and OpsGenie integration
- [ ] Slack and Teams alert notifications
- [ ] Incident history analytics dashboard
- [ ] Auto-remediation scripts execution
- [ ] Multi-model support (GPT-4, Claude)
- [ ] Prometheus and Grafana integration
- [ ] Email alert summaries

---

## 👨‍💻 About the Developer

**Aditya Sarap** — AI Developer | MCA Data Science | Pune, India

Building production-grade AI systems that solve real business problems.

[![Portfolio](https://img.shields.io/badge/Portfolio-Live-2E75B6?style=for-the-badge)](https://ai-portfolio-i4cj.onrender.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/aditya-sarap)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-1F4E79?style=for-the-badge&logo=github)](https://github.com/wyldex3ml-pro)

**Other Live Projects:**

| Project | Live Demo |
|---|---|
| AI Automation Hub — Email Intelligence | [Live](https://ai-automation-hub-production.up.railway.app) |
| VigilanceAI — Surveillance Platform | [Live](https://wyldex3ml-pro-vigilanceai-dashboard-q9celx.streamlit.app) |
| AI Developer Portfolio | [Live](https://ai-portfolio-i4cj.onrender.com) |

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**⭐ If this project impressed you, please give it a star!**

<br/>

[![Live API](https://img.shields.io/badge/🚀%20Try%20Live%20API-2E75B6?style=for-the-badge)](https://aegis-ai-cr2u.onrender.com)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2E75B6,100:060E1F&height=100&section=footer" width="100%"/>

</div>
