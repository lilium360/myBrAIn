import threading
import time
import json
import datetime
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from core import config
from core.db import BrainDB
from core.analyzer import ProjectAnalyzer

class SilentObserver(threading.Thread):
    def __init__(self, data_dir: Path, active_workbase: dict = None, interval: int = 300):
        super().__init__()
        self.data_dir = data_dir
        self.interval = interval
        self.state_file = data_dir / "observer_state.json"
        self.daemon = True
        self.stop_event = threading.Event()
        
        self.db = None # Lazy init to avoid issues with thread affinity if any
        self.analyzer = ProjectAnalyzer()
        self.active_workbase = active_workbase or {}
        
        # Initial state
        self.state = {
            "status": "Starting",
            "last_run": "Never",
            "checked_files": 0,
            "drift_detected": False,
            "logs": ["Observer thread initialized."]
        }
        self._write_state()

    def _log(self, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.state["logs"] = [log_entry] + self.state["logs"][:4]
        # Never print to stdout as it breaks MCP protocol
        print(f"SILENT_OBSERVER: {log_entry}", file=sys.stderr)

    def _write_state(self):
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"FAILED TO WRITE OBSERVER STATE: {e}", file=sys.stderr)

    def run(self):
        self.db = BrainDB()
        self._log("Observer daemon started.")
        
        while not self.stop_event.is_set():
            try:
                self.state["status"] = "Running"
                self._write_state()
                
                self._perform_scan()
                
                self.state["status"] = "Sleeping"
                self.state["last_run"] = datetime.datetime.now().isoformat()
                self._write_state()
                
                # Wait for interval or stop event
                if self.stop_event.wait(self.interval):
                    break
                    
            except Exception as e:
                self.state["status"] = "Error"
                self._log(f"Error in scan loop: {e}")
                self._write_state()
                if self.stop_event.wait(60): # Retry after 1 min on error
                    break

    def _perform_scan(self):
        self._log("Starting codebase scan...")
        
        # Read the active workbase set by MCP tools
        wb_id = self.active_workbase.get("workbase_id")
        root_path_str = self.active_workbase.get("root_path", "")
        project_name = self.active_workbase.get("project_name", "Unknown")
        
        if not wb_id:
            self._log("No active workbase yet. Waiting for first tool call.")
            self.state["drift_detected"] = False
            return
        
        if not root_path_str:
            self._log(f"Active workbase '{project_name}' has no root_path. Skipping.")
            self.state["drift_detected"] = False
            return
        
        root = Path(root_path_str)
        if not root.exists() or not root.is_dir():
            self._log(f"Path for '{project_name}' not accessible. Skipping.")
            self.state["drift_detected"] = False
            return
        
        # Retrieve rules for the active workbase
        rules = self.db.get_rules(wb_id)
        
        if not rules:
            self._log(f"No rules for '{project_name}'. Skipping.")
            self.state["drift_detected"] = False
            return
        
        self._log(f"Scanning '{project_name}' ({len(rules)} rules)...")
        
        drifts_found = 0
        files_checked = 0
        
        for p in root.rglob("*"):
            if self.stop_event.is_set(): return
            
            if p.is_file() and p.suffix.lower() in [".py", ".js", ".ts", ".go", ".rs"]:
                if any(ignored in p.parts for ignored in config.IGNORED_DIRS):
                    continue
                
                files_checked += 1
                drifts = self.analyzer.detect_memory_drift(p, rules)
                if drifts:
                    drifts_found += len(drifts)
                    for d in drifts:
                        self._log(f"Drift in {project_name}/{p.name}: {d['drift_type']}")
        
        self.state["checked_files"] = files_checked
        self.state["drift_detected"] = drifts_found > 0
        self._log(f"Scan complete. {files_checked} files, {drifts_found} drifts.")

    def stop(self):
        self.stop_event.set()
