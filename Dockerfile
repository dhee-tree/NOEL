# ==========================================
# Stage 1: Builder (Compiling dependencies)
# ==========================================
FROM python:3.13-slim-bookworm as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Install SYSTEM BUILD dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Create virtual environment
RUN python -m venv /opt/venv
# Activate venv for the build stage
ENV PATH="/opt/venv/bin:$PATH"

# 3. Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Final (Runtime image)
# ==========================================
FROM python:3.13-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# 1. Install SYSTEM RUNTIME dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# 3. Copy project files
COPY . /app/

# 4. Security: Create a non-root user
# Running as root in production is a security risk.
RUN addgroup --system django && \
    adduser --system --ingroup django django && \
    chown -R django:django /app

# 5. Make entrypoint executable
RUN chmod +x /app/scripts/entrypoint/entrypoint.sh

# Switch to non-root user
USER django

EXPOSE 8000
