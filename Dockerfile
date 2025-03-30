FROM python:3.12-slim

WORKDIR /app

# Create non-root user early to avoid rebuilding large layers
RUN useradd -m appuser

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m pip install semgrep

# Create directories with correct permissions
RUN mkdir -p temp_uploads temp_code results configs \
    && chown -R appuser:appuser /app \
    && chmod 755 temp_uploads temp_code results configs

# Copy application code with correct ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 8501

ENV PYTHONPATH=/app \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/ || exit 1

CMD ["streamlit", "run", "app.py"]