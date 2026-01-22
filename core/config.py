from pathlib import Path

# Single source of truth for configuration
BASE_DATA_DIR = Path("~/mybrain_data").expanduser().resolve()
CHROMA_COLLECTION = "mybrain_memory"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

DB_SCHEMA_VERSION = 1

DB_LOCK_RETRY_SECONDS = 2
DB_LOCK_RETRY_INTERVAL = 0.1

MAX_TREE_LINES = 200
MAX_FILE_SIZE_BYTES = 1_000_000
MAX_STYLE_SAMPLE_FILES = 3

# Vector search threshold for semantic conflict detection (lower distance = higher similarity)
CONFLICT_DISTANCE_THRESHOLD = 0.5  # cosine distance

IGNORED_DIRS = {
    "node_modules", ".git", "__pycache__", "venv", ".env",
    "dist", "build", ".idea", ".vscode"
}

# Known binary or irrelevant extensions to ignore for code analysis
BINARY_EXTENSIONS = {
    # Images & Media
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
    # Archives & Executables
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".exe", ".dll", ".so", ".bin", ".iso",
    # Binary Docs & Fonts
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".ttf", ".otf", ".woff", ".woff2",
    # Databases & Cache
    ".sqlite", ".db", ".pyc", ".class"
}
