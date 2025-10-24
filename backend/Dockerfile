# Multi-stage build for optimal image size

# Stage 1: Build stage
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
# Extract dependencies from pyproject.toml and install them
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    "fastapi[standard]>=0.118.2,<0.119.0" \
    "uvicorn>=0.37.0,<0.38.0" \
    "python-dotenv>=1.1.1,<2.0.0" \
    "sqlalchemy>=2.0.43,<3.0.0" \
    "alembic>=1.16.5,<2.0.0" \
    "psycopg2-binary>=2.9.10,<3.0.0" \
    "python-jose[cryptography]>=3.3.0,<4.0.0" \
    "python-multipart>=0.0.19,<1.0.0" \
    "google-api-python-client>=2.147.0,<3.0.0" \
    "google-auth-httplib2>=0.2.0,<1.0.0" \
    "google-auth-oauthlib>=1.2.1,<2.0.0" \
    "pydantic-settings>=2.5.0,<3.0.0" \
    "bcrypt<4.0.0" \
    "passlib[bcrypt]>=1.7.4"

# Stage 2: Runtime stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (Cloud Run will set PORT env variable)
ENV PORT=8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health').read()"

# Start command
# Cloud Run will provide PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1
