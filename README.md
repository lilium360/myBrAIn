# 🧠 myBrAIn — MCP Ecosystem

**Deterministic, Idempotent, Context-Aware Second Brain for Google Antigravity.**

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-lightgrey)
![MCP](https://img.shields.io/badge/MCP-Server-orange)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![MIT License](https://img.shields.io/badge/license-MIT-green.svg)

---

## Introduction
**myBrAIn** is an MCP (Model Context Protocol) server designed to provide persistent and contextual memory to language models (like Google Antigravity). It acts as a "second brain" for your development environment, allowing the AI to remember project rules, architectural decisions, and technical insights across different chat sessions.

---

## System Architecture
The system is divided into three main components:
*   **Core**: Manages persistence (`db.py`) and analytical intelligence (`analyzer.py`) for extracting insights from code.
*   **Server**: The standard MCP interface (`server.py`) that allows Antigravity to interact with the brain.
*   **Admin UI**: An intuitive dashboard (`admin.py`) based on Streamlit to visualize, manage, and debug stored memories.

---

## 🏗 Installation

### A. Docker Deployment (Recommended)
The easiest way to run **myBrAIn** is using Docker Compose.

```bash
# Clone & Prepare
git clone https://github.com/lilium360/myBrAIn.git
cd myBrAIn
cp .env.example .env

# Spin up
docker compose up -d
```
The Admin UI will be available at: **[http://localhost:8501](http://localhost:8501)**

### B. Local Installation (Native Python)
1.  **Clone & Enter**:
    ```bash
    git clone https://github.com/lilium360/myBrAIn.git
    cd myBrAIn
    ```
2.  **Setup Environment**:
    *   Windows: `python -m venv venv && .\venv\Scripts\activate`
    *   Unix: `python3 -m venv venv && source venv/bin/activate`
3.  **Install**: `pip install -r requirements.txt`

---

## 🚀 Usage Guide

### 1. Launching the Admin Dashboard
To graphically manage the database and visualize insights:

*   **Via Docker**: Already running after `docker compose up`. Open **http://localhost:8501**.
*   **Via Python**: Run `streamlit run admin.py` (or `python -m streamlit run admin.py`).

### 2. Integration in IDEs (Cursor, VS Code + Antigravity)
Add this to your `mcpServers` configuration JSON:

#### Option A: Via Docker
```json
{
  "mcpServers": {
    "mybrain": {
      "command": "docker",
      "args": ["exec", "-i", "mybrain-admin", "python", "server.py"],
      "env": {
        "MYBRAIN_DATA_DIR": "/data/mybrain"
      }
    }
  }
}
```

#### Option B: Via Python (Local)
```json
{
  "mcpServers": {
    "mybrain": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/mybrain/server.py"]
    }
  }
}
```
> [!IMPORTANT]
> Change the path in `args` to the **ABSOLUTE** path on your machine.

---

## 🧠 Project Onboarding & Context
**myBrAIn** is specifically designed to handle "Project Onboarding" — a process where the AI analyzes your current codebase and stores its architectural DNA.

### How to Onboard a New Project
Once you have the MCP server configured, simply use the following prompt:

> "I want to perform a full onboarding of this project into your long-term memory. Sequentially perform: Structural Link, Stack Analysis, Architectural Analysis, Style Analysis, and Exclusion Analysis."

---

## Available Tools
- `initialize_workbase`: Link a directory to the brain.
- `store_insight`: Manually save a rule or context.
- `recall_context`: Retrieve relevant memories for the current task.
- `critique_code`: Validate code against stored architectural rules.

---

## Advanced Configuration
You can customize the system behavior via environment variables (in Docker) or by modifying `core/config.py`.

---

## Roadmap & Limitations
*   **Core v1**: Focused on vector persistence and code analysis.
*   **Graph Visualization**: (Planned) Visualization of relationships between insights.
*   **Vector-Based Conflict Detection**: Identified potentially contradictory insights.
