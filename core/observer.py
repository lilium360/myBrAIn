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
    def __init__(self, data_dir: Path, interval: int = 300):
        super().__init__()
        self.data_dir = data_dir
        self.interval = interval
        self.state_file = data_dir / "observer_state.json"
        self.daemon = True
        self.stop_event = threading.Event()
        
        self.db = None # Lazy init to avoid issues with thread affinity if any
        self.analyzer = ProjectAnalyzer()
        
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
        
        # In a real scenario, we would iterate over workbases
        # For now, we use the current directory as a proxy for the primary workbase
        root = Path(".").resolve()
        
        # Retrieve rules
        # We need a way to get workbase_id without interactive user context
        # Heuristic: search for directories that have been initialized in DB
        # For simplicity, we'll scan the root and use its ID if it exists
        workbase_id = str(root)
        rules = self.db.get_rules(workbase_id)
        
        if not rules:
            self._log("No architectural rules found. Skipping scan.")
            self.state["drift_detected"] = False
            return

        drifts_found = 0
        files_checked = 0
        
        # Scan files
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
                        self._log(f"Drift detected in {p.name}: {d['drift_type']}")
        
        self.state["checked_files"] = files_checked
        self.state["drift_detected"] = drifts_found > 0
        self._log(f"Scan complete. Checked {files_checked} files. Found {drifts_found} drifts.")

    def stop(self):
        self.stop_event.set()
