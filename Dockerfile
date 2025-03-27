FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install semgrep
RUN python -m pip install semgrep

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Setup directories and permissions
RUN mkdir -p temp_uploads temp_code results configs \
    && chmod 755 temp_uploads temp_code results configs

# Security: Create non-root user
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

ENV PYTHONPATH=/app \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["streamlit", "run", "app.py"]