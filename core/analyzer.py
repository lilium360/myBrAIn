import os
from pathlib import Path
from typing import Dict, List, Any
import collections

from core import config

class ProjectAnalyzer:
    def __init__(self):
        self.ignored_dirs = config.IGNORED_DIRS
        self.allowed_extensions = config.ALLOWED_EXTENSIONS

    def normalize_path(self, path: str) -> Path:
        """Resolve and validate the given path."""
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise ValueError(f"Path does not exist: {p}")
        if not p.is_dir():
            raise ValueError(f"Path is not a directory: {p}")
        return p

    def scan_structure(self, root_path: Path) -> str:
        """Generate a deterministic text-based tree of the project structure."""
        tree_lines = []
        count = 0
        
        # Sort for determinism
        for root, dirs, files in os.walk(root_path):
            # Resolve root to Path object and handle symlinks as requested
            curr_root = Path(root).resolve()
            
            # Skip if we escaped the root
            if not str(curr_root).startswith(str(root_path)):
                continue

            # In-place modification of dirs to skip ignored ones
            dirs[:] = sorted([d for d in dirs if d not in self.ignored_dirs])
            files = sorted(files)

            level = len(curr_root.relative_to(root_path).parts)
            indent = "  " * level
            
            if curr_root == root_path:
                tree_lines.append(f"{curr_root.name}/")
            else:
                tree_lines.append(f"{indent}{curr_root.name}/")
            
            count += 1
            if count >= config.MAX_TREE_LINES:
                break

            sub_indent = "  " * (level + 1)
            for f in files:
                file_path = curr_root / f
                if file_path.suffix.lower() in self.allowed_extensions:
                    if file_path.stat().st_size <= config.MAX_FILE_SIZE_BYTES:
                        tree_lines.append(f"{sub_indent}{f}")
                        count += 1
                
                if count >= config.MAX_TREE_LINES:
                    break
            
            if count >= config.MAX_TREE_LINES:
                break
                
        return "\n".join(tree_lines)

    def detect_style(self, root_path: Path) -> Dict[str, str]:
        """Infer coding style (indentation and naming convention) from sample files."""
        indentation = "unknown"
        naming = "unknown"
        
        sample_files = []
        for root, _, files in os.walk(root_path):
            curr_root = Path(root).resolve()
            # Skip ignored dirs
            if any(part in self.ignored_dirs for part in curr_root.relative_to(root_path).parts):
                continue
                
            for f in files:
                file_path = curr_root / f
                if file_path.suffix.lower() in {".py", ".js", ".ts"}:
                    sample_files.append(file_path)
                    if len(sample_files) >= config.MAX_STYLE_SAMPLE_FILES:
                        break
            if len(sample_files) >= config.MAX_STYLE_SAMPLE_FILES:
                break

        if not sample_files:
            return {"indentation": indentation, "naming": naming}

        # Analyze indentation
        indent_counts = collections.Counter()
        for f_path in sample_files:
            try:
                with open(f_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("  "):
                            # Count leading spaces
                            spaces = len(line) - len(line.lstrip(' '))
                            if spaces > 0:
                                indent_counts[spaces] += 1
                        elif line.startswith("\t"):
                            indent_counts["tab"] += 1
            except Exception:
                continue

        if indent_counts:
            most_common = indent_counts.most_common(1)[0][0]
            if most_common == "tab":
                indentation = "tabs"
            else:
                indentation = f"{most_common} spaces"

        # Analyze naming (simplified heuristic)
        naming_counts = collections.Counter()
        for f_path in sample_files:
            try:
                with open(f_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "_" in content:
                        naming_counts["snake_case"] += 1
                    if any(c.isupper() for c in content) and "_" not in content:
                        naming_counts["camelCase"] += 1
            except Exception:
                continue
        
        if naming_counts:
            naming = naming_counts.most_common(1)[0][0]

        return {
            "indentation": indentation,
            "naming": naming
        }
