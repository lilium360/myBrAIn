import sys
import hashlib
import json
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from core.config import CONFLICT_DISTANCE_THRESHOLD
from core.db import BrainDB
from core.analyzer import ProjectAnalyzer

# Initialize MCP server
mcp = FastMCP("myBrAIn")

# Initialize components
db = BrainDB()
analyzer = ProjectAnalyzer()

def get_workbase_id(root_path: Path) -> str:
    """Generate a deterministic hash for a path (cross-platform safe)."""
    # Use lowercase for hash calculation to be case-insensitive
    normalized = str(root_path).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

@mcp.tool()
def initialize_workbase(root_path: str) -> dict:
    """
    Validate, normalize and analyze a project directory.
    Creates or updates the workbase context.
    """
    try:
        path = analyzer.normalize_path(root_path)
        workbase_id = get_workbase_id(path)
        
        # Analyze project
        structure = analyzer.scan_structure(path)
        style = analyzer.detect_style(path)
        
        # Save context to DB
        metadata = {
            "workbase_id": workbase_id,
            "project_name": path.name,
            "type": "context",
            "category": "project_structure",
            "source": "agent"
        }
        
        # Update/Add context
        db.add_memory(
            memory_id=f"context_{workbase_id}",
            text=f"Structure:\n{structure}\n\nStyle:\n{json.dumps(style)}",
            metadata=metadata
        )
        
        return {
            "workbase_id": workbase_id,
            "status": "linked",
            "style": style
        }
    except Exception as e:
        print(f"Error initializing workbase: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}

@mcp.tool()
def store_insight(content: str, category: str, workbase_id: str, force: bool = False, replace_id: Optional[str] = None) -> dict:
    """
    Store a project rule or insight.
    Performs semantic conflict detection before saving.
    If replace_id is provided, it deletes that memory before storing the new one (Atomic Update).
    """
    try:
        # If explicit replacement is requested
        if replace_id:
            try:
                db.delete_memory(replace_id)
            except Exception:
                pass # ID might not exist or already deleted

        # Conflict Detection (within the same category if possible)
        conflict = db.check_conflict(content, workbase_id, category=category)
        
        if conflict and not force and not replace_id:
            return {
                "status": "conflict",
                "memory_id": conflict["id"],
                "similar_rule": conflict["text"],
                "distance": conflict["distance"],
                "message": "A similar or conflicting rule already exists in this category. Use force=True to override or provide replace_id."
            }
        
        # If force is True and a conflict was found, delete the old one
        if force and conflict:
            db.delete_memory(conflict["id"])
        
        # Generate deterministic ID for the rule
        rule_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
        memory_id = f"rule_{workbase_id}_{rule_hash}"
        
        metadata = {
            "workbase_id": workbase_id,
            "type": "rule",
            "category": category,
            "source": "manual" if force else "agent"
        }
        
        db.add_memory(memory_id, content, metadata)
        
        return {
            "status": "stored",
            "memory_id": memory_id,
            "replaced": bool(replace_id or (force and conflict)),
            "conflict_resolved": bool(conflict)
        }
    except Exception as e:
        print(f"Error storing insight: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}

@mcp.tool()
def recall_context(query: str, workbase_id: str) -> dict:
    """
    Retrieve relevant project rules and context for a query.
    """
    try:
        results = db.search(query, workbase_id, limit=5)
        
        memories = []
        if results["ids"]:
            for i in range(len(results["ids"][0])):
                memories.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "category": results["metadatas"][0][i].get("category", "unknown"),
                    "type": results["metadatas"][0][i].get("type", "unknown")
                })
        
        return {"results": memories}
    except Exception as e:
        print(f"Error recalling context: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}

@mcp.tool()
def critique_code(code_snippet: str, workbase_id: str) -> dict:
    """
    Analyze a code snippet against stored project rules.
    """
    try:
        # In a real scenario, this would involve LLM reasoning.
        # For Core v1, we perform semantic search to find relevant rules.
        relevant_rules = db.search(code_snippet, workbase_id, limit=3, category=None)
        
        violations = []
        if relevant_rules["ids"]:
            for i in range(len(relevant_rules["ids"][0])):
                # Heuristic: if distance is small, it's a "relevant rule" that might be violated
                # In Core v1, we return these as potential matches to check against.
                violations.append({
                    "rule": relevant_rules["documents"][0][i],
                    "severity": "info",
                    "message": "Review this snippet against the found project pattern."
                })
        
        return {"violations": violations}
    except Exception as e:
        print(f"Error critiquing code: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}

@mcp.tool()
def audit_codebase(directory_path: Optional[str] = None) -> dict:
    """
    Scan the codebase for architectural drift against stored memories.
    Identifies contradictions and suggests self-healing updates.
    """
    try:
        root = analyzer.normalize_path(directory_path or ".")
        workbase_id = get_workbase_id(root)
        
        # Retrieve architecture and constraint rules
        all_rules = db.get_rules(workbase_id)
        architectural_rules = [
            r for r in all_rules 
            if r["metadata"].get("category") in ["architecture", "constraints", "coding_style"]
        ]
        
        if not architectural_rules:
            return {"status": "info", "message": "No architectural rules found for this workbase."}
            
        drifts = []
        # Scan files (limited to relevant extensions)
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in [".py", ".js", ".ts", ".go", ".rs"]:
                if any(ignored in p.parts for ignored in analyzer.ignored_dirs):
                    continue
                
                file_drifts = analyzer.detect_memory_drift(p, architectural_rules)
                drifts.extend(file_drifts)
        
        report = []
        for d in drifts:
            report.append(f"DRIFT in `{d['file']}`: Rule '{d['rule_text']}' violated. Evidence: {d['evidence']}")
            
        summary = "No drift detected."
        if drifts:
            summary = f"Detected {len(drifts)} architectural drifts."
            
        return {
            "status": "success",
            "summary": summary,
            "drifts": drifts,
            "report": "\n".join(report)
        }
    except Exception as e:
        print(f"Error auditing codebase: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    from core.observer import SilentObserver
    from core import config
    
    # Start the Silent Observer background thread
    observer = SilentObserver(data_dir=config.BASE_DATA_DIR)
    observer.start()
    
    # Ensure stdout is never used for logs
    # FastMCP handles this internally, but we enforce it just in case.
    mcp.run()
