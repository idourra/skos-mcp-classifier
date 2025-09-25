# Multi-stage build for SKOS MCP Classifier
FROM python:3.8-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY server/requirements.txt ./server/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r server/requirements.txt

# Copy source code
COPY server/ ./server/
COPY data/ ./data/
COPY skos.sqlite ./ 

# Initialize database if needed
RUN if [ ! -f server/skos.sqlite ]; then \
        python server/skos_loader.py && \
        cp skos.sqlite server/; \
    fi

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash skos && \
    chown -R skos:skos /app
USER skos

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Default command
CMD cd server && uvicorn main:app --host 0.0.0.0 --port 8000