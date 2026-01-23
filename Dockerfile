# myBrAIn Docker Image
# Multi-purpose image for both MCP server and Admin UI

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies for chromadb and sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /data/mybrain

# Default environment variables
ENV MYBRAIN_DATA_DIR=/data/mybrain \
    MYBRAIN_EMBEDDING_MODEL=all-MiniLM-L6-v2 \
    MYBRAIN_CONFLICT_THRESHOLD=0.5

# Expose Streamlit port
EXPOSE 8501

# Health check for admin UI
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Default: run admin UI
CMD ["streamlit", "run", "admin.py", "--server.address=0.0.0.0", "--server.port=8501"]
