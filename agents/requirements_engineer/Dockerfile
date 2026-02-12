FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY common/ /app/common/
COPY agents/requirements_engineer/ /app/

# Set environment variables
ENV PYTHONPATH=/app
ENV CONFIG_PATH=/app/config.yaml

# Create log directory
RUN mkdir -p /var/log/agents

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the agent
CMD ["python", "-m", "agents.requirements_engineer.agent"]
