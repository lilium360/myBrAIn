# 🧠 myBrAIn — MCP Ecosystem

**Deterministic, Idempotent, Context-Aware Second Brain for Google Antigravity.**

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-lightgrey)
![MCP](https://img.shields.io/badge/MCP-Server-orange)
![MIT License](https://img.shields.io/badge/license-MIT-green.svg)

---

## Introduction
**myBrAIn** is an MCP (Model Context Protocol) server designed to provide persistent and contextual memory to language models (like Google Antigravity). It acts as a "second brain" for your development environment, allowing the AI to remember project rules, architectural decisions, and technical insights across different chat sessions.

### Core Principles
1.  **Idempotency**: Uses a deterministic Hash ID system to avoid duplicates and ensure data consistency.
2.  **Security**: Designed to operate in MCP environments; logs are sent exclusively to *Stderr* to avoid polluting the *Stdout* channel used by the protocol.
3.  **Robustness**: Built-in *Vector Conflict Detection* system to prevent the storage of conflicting information.

---

## System Architecture
The system is divided into three main components:
*   **Core**: Manages persistence (`db.py`) and analytical intelligence (`analyzer.py`) for extracting insights from code.
*   **Server**: The standard MCP interface (`server.py`) that allows Antigravity to interact with the brain.
*   **Admin UI**: An intuitive dashboard (`admin.py`) based on Streamlit to visualize, manage, and debug stored memories.

---

## 🛠 Installation (Step-by-Step)

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/lilium360/myBrAIn.git
    cd mybrain
    ```

2.  **Create virtual environment**:
    *   **Windows**:
        ```powershell
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   **Mac/Linux**:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🐳 Docker Deployment

The easiest way to run **myBrAIn** is using Docker Compose. This starts both the Streamlit Admin UI and prepares the MCP server environment.

### Quick Start
```bash
# 1. Clone the repository (if not already done)
git clone https://github.com/Labontese/myBrAIn.git
cd myBrAIn

# 2. Prepare environment (optional)
cp .env.example .env

# 3. Spin up the ecosystem
docker compose up -d
```

### Accessing the Dashboard
The Admin UI will be available at: **[http://localhost:8501](http://localhost:8501)**

### Integration in IDEs (Cursor, VS Code + Antigravity)
To use the MCP server from within your IDE while it's running in Docker, add this to your `mcpServers` configuration:

```json
{
  "mcpServers": {
    "mybrain": {
      "command": "docker",
      "args": ["exec", "-i", "mybrain-mcp", "python", "server.py"],
      "env": {
        "MYBRAIN_DATA_DIR": "/data/mybrain"
      }
    }
  }
}
```

---

## 🚀 Project Onboarding & Context

**myBrAIn** is specifically designed to handle "Project Onboarding" — a process where the AI analyzes your current codebase and stores its architectural DNA, coding patterns, and constraints in its persistent memory.

### How to Onboard a New Project
Once you have the MCP server configured in your IDE, simply use the following prompt to let **myBrAIn** index your project:

> "I want to perform a full onboarding of this project into your long-term memory. Sequentially perform: Structural Link, Stack Analysis, Architectural Analysis, Style Analysis, and Exclusion Analysis."

### Available Tools
- `initialize_workbase`: Link a directory to the brain.
- `store_insight`: Manually save a rule or context.
- `recall_context`: Retrieve relevant memories for the current task.
- `critique_code`: Validate code against stored architectural rules.

---

## Advanced Configuration
You can customize the system behavior (similarity thresholds, database paths, embedding models) by modifying the file:
`mybrain/core/config.py`

---

## Roadmap & Limitations
*   **Core v1**: Currently focused on vector persistence and code analysis.
*   **Graph Visualization**: (Planned) Visualization of relationships between insights.
*   **Vector-Based Conflict Detection**: Uses cosine similarity to identify potentially contradictory insights.
