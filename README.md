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
*   **Admin UI**: A premium dashboard (`admin.py`) based on Streamlit to visualize, manage, and debug stored memories with advanced features like **Knowledge Graphs**, **Memory Export**, and the **Silent Observer** dashboard.
*   **Observer**: A background daemon thread (`observer.py`) that monitors codebase drift in real-time.

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

### 📝 Integration Protocol (MANDATORY for AI Agents)
To ensure the AI uses **myBrAIn** correctly and consistently, copy and paste the following instructions into your project's custom instructions or `.cursorrules` file:

```markdown
# myBrAIn Integration Protocol (MANDATORY)

You are connected to **myBrAIn**, an MCP server that acts as your Long-Term Memory and "Single Source of Truth" for this project.
You MUST NEVER rely solely on the current chat context or your general knowledge when project-specific rules are saved.

Strictly follow this operational cycle for EVERY interaction:

## 1. RECALL PHASE (Before Reasoning)
BEFORE generating any code or technical response, you MUST consult the memory:
- **Action:** Run `recall_context` using relevant keywords (e.g., "auth logic", "styling conventions", "api patterns").
- **Goal:** Retrieve the tech stack, architectural rules, and standard components already defined.
- **Constraint:** If you find an existing rule or component (e.g., "Always use `CustomButton`"), you MUST use it. Creating duplicates or unauthorized variations is FORBIDDEN.

## 2. CONSISTENCY PHASE (During Reasoning)
While generating the response:
- Strictly adhere to retrieved Constraints.
- If the user requests something that violates a saved rule (e.g., "Use jQuery" in a React project saved as "No jQuery"), warn the user of the conflict before proceeding.
- Use the code style (naming, comments, structure) retrieved from memory to maintain uniformity.

## 3. MEMORIZATION PHASE (During/After Action)
Your task is to keep the memory alive and updated. DO NOT wait for the user to ask.
Use `store_insight` proactively in the following cases:
- **New Decisions:** If a new architectural rule is established (e.g., "From now on, use only Tailwind").
- **New Patterns:** If you write a reusable generic component, save it as a "Standard Component".
- **Corrections:** If the user corrects your error, save the correction (e.g., "Do not use library X because it's buggy").
- **Onboarding:** If you detect a new empty project, propose or run `initialize_workbase`.

## 4. CONFLICT MANAGEMENT
- **myBrAIn Priority:** If your general knowledge suggests "X" but myBrAIn says "Y", the correct answer is "Y".
- **Updates:** If an old memory is obsolete, use `store_insight` to overwrite it (the system handles semantic collision automatically via `replace_id`).

---
**Correct Workflow Example:**
User: "Create a login page."
AI (Internal Thought): "Check myBrAIn for 'login', 'auth', 'ui components'."
AI Action: `recall_context("login auth ui style")`
AI (Found): "The project uses NextAuth and Shadcn components."
AI Response: Generates code using EXACTLY NextAuth and Shadcn, without inventing custom CSS unless necessary.
AI Action (Post): Since a new useful auth hook was created, run `store_insight` to save it.
```

---

## Available Tools
- `initialize_workbase`: Link a directory to the brain.
- `store_insight`: Manually save a rule or context.
- `recall_context`: Retrieve relevant memories for the current task.
- `critique_code`: Validate code against stored architectural rules.
- `audit_codebase`: Scan the entire codebase for architectural drift and contradictions.

---

## Advanced Configuration
You can customize the system behavior via environment variables (in Docker) or by modifying `core/config.py`.

---

---

## 🗂️ Admin Dashboard Features (v1.1)
The refactored Admin Dashboard includes:
- **Card-Based Explorer**: Browse memories in a modernized grid with colored tags for rules, context, and constraints.
- **Knowledge Graph**: Interactively visualize the semantic relationships and categorical clusters of your brain.
- **Bulk Operations**: Select multiple records for simultaneous deletion or quick editing.
- **Silent Observer Dashboard**: Real-time status monitoring of the background drift detection engine.
- **Memory Management**: Export full brain dumps or workbase-specific JSONs; import and reassign knowledge packets between projects.
- **Workbase Management**: Securely manage project data with a confirmation-protected destruction mechanism.

---

## 🔮 Roadmap
- [ ] **Semantic Roadmap:** Internal task planner to maintain context on long-term goals and feature progress.
- [x] **Memory Import/Export:** Share your "brain" with your team (Granular & Targetable).
- [x] **Silent Observer:** Background daemon that scans code and detects architectural drift.
- [x] Docker Support
- [x] Admin UI with Knowledge Graph