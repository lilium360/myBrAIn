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
    git clone <repository-url>
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

## 🚀 Usage Guide

### A. Launching the Admin Dashboard
To graphically manage the database and visualize insights:
*   **Main Command**: `streamlit run admin.py`
*   **Windows Troubleshooting**: If the command above is not recognized, use: `python -m streamlit run admin.py`
*   **Mac/Linux Troubleshooting**: `python3 -m streamlit run admin.py`

### B. Integration in Google Antigravity / Cursor
To enable myBrAIn, you need to add the configuration to the MCP servers JSON file (`mcpServers`).

> [!IMPORTANT]
> In the JSON block below, the path in `args` must be **ABSOLUTE** and point to the `server.py` file within your project folder.

```json
{
    "mcpServers": {
        "mybrain": {
            "command": "python",
            "args": [
                "D:/Documenti/Augment Project/mybrain/server.py"
            ]
        }
    }
}
```

> [!WARNING]
> **Ensure you replace the example path with the real path of the `mybrain` folder on your disk (use `/` or `\\` on Windows).**

---

### C. Project Onboarding (Recommended)
To perform a complete onboarding of a new project into **myBrAIn**, copy and paste the following prompt into your chat with Antigravity/Cursor. This ensures the brain is correctly initialized with the project's tech stack, architecture, and coding style.

> **Note:** Ensure you have already configured the MCP server in your JSON settings as described in step B.

**Copy-Paste Template:**
```text
Activate the mybrain MCP server.
I want to perform a full onboarding of this project into your long-term memory.

Perform these steps sequentially:

1. Structural Link  
   Call initialize_workbase on the current directory (use the absolute path).

2. Stack Analysis  
   Read dependency files (requirements.txt, pyproject.toml, or package.json).  
   Identify the main technologies and save them using store_insight with category="tech_stack".

3. Architectural Analysis  
   Read the 2-3 main core logic files.  
   Deduce the architecture (e.g., MVC, Clean Architecture, Repository Pattern).  
   Save the architectural rules using store_insight with category="architecture".  
   Specify whether the rules are Observed or Declared.

4. Style Analysis  
   Analyze comments, naming, error handling, and function structure.  
   Save preferences with store_insight and category="coding_style".  
   Specify whether they are Observed or Declared.

5. Exclusion Analysis  
   Identify patterns or technologies commonly used but absent in this project.  
   Save this information as constraints with category="constraints".

Upon completion:
- Confirm completion.
- Show a structured summary of the saved memories (by category).
- Indicate the workbase_id used.
```

---

## MCP Features (Tools)
Once configured, Antigravity will have access to the following tools:

*   `initialize_workbase`: Analyzes and indexes the current working directory.
*   `store_insight`: Stores a new rule or discovery (includes automatic conflict detection).
*   `recall_context`: Retrieves the most relevant information based on the current query.
*   `critique_code`: Analyzes a code snippet by comparing it against stored style and architecture rules.

---

## Advanced Configuration
You can customize the system behavior (similarity thresholds, database paths, embedding models) by modifying the file:
`mybrain/core/config.py`

---

## Roadmap & Limitations
*   **Core v1**: Currently focused on vector persistence and code analysis.
*   **Graph Visualization**: (Planned) Visualization of relationships between insights.
*   **Vector-Based Conflict Detection**: Uses cosine similarity to identify potentially contradictory insights.
