# Hermes - Multi-stage Containerfile for OpenShift
# Uses Red Hat UBI9 Python 3.11 base image (cached in internal registry)

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python-311:latest AS builder

# Set working directory
WORKDIR /tmp/build

# Copy requirements first for layer caching
COPY requirements.txt .

# Install dependencies (UBI9 Python uses virtualenv, so no --user flag needed)
RUN pip install --no-cache-dir -r requirements.txt


# ============================================================================
# Stage 2: Runtime
# ============================================================================
FROM python-311:latest

# Metadata
LABEL name="hermes" \
      vendor="Red Hat OCTO" \
      version="1.0.0" \
      summary="Hermes - OCTO Emerging Technologies Playbook System" \
      description="AI-powered prototype generation and technology transfer system for Red Hat OCTO team"

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder (virtualenv location)
COPY --from=builder /opt/app-root /opt/app-root

# Copy application code
COPY --chown=1001:0 . /app/

# Ensure Python can find installed packages
ENV PYTHONPATH="/app:$PYTHONPATH" \
    PYTHONUNBUFFERED=1

# Create directories with proper permissions
RUN mkdir -p /app/output /app/static /app/templates && \
    chown -R 1001:0 /app && \
    chmod -R g=u /app

# Switch to non-root user
USER 1001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5.0)" || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
