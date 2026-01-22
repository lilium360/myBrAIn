# myBrAIn — Core v1

Deterministic, Idempotent, Vector-Conflict-Aware Second Brain MCP Server.

## Features
- **Deterministic Workbases**: Projects are linked via stable hashes of their absolute paths.
- **Semantic Consistency**: Conflict detection prevents redundant or contradictory project rules using vector similarity.
- **Project Intelligence**: Automatic style detection (indentation, naming) and structure analysis.
- **Persistent Memory**: Uses ChromaDB for reliable, local vector storage.
- **Admin Dashboard**: Streamlit-based UI for manual memory management.

## Setup

### 1. Installation
Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration for Antigravity/Cursor
Add the following to your MCP configuration JSON:

```json
{
    "mcpServers": {
        "mybrain": {
            "command": "python",
            "args": [
                "d:/Documenti/Augment Project/mybrain/server.py"
            ]
        }
    }
}
```

### 3. Running Admin UI
To manage memories manually:
```bash
streamlit run admin.py
```

## Tools
- `initialize_workbase(root_path)`: Set up or update project context.
- `store_insight(content, category, workbase_id, force)`: Save a project rule with conflict checks.
- `recall_context(query, workbase_id)`: Find relevant project memory.
- `critique_code(code_snippet, workbase_id)`: Validate code against project rules.

## Core v1 Constraints
- No stdout usage (all logs to stderr).
- Absolute paths only.
- Local persistence in `~/mybrain_data`.
