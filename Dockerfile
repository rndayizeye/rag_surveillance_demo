# =============================================================================
# Stage 1 — builder
# =============================================================================
# A temporary stage that installs dependencies into an isolated prefix.
# Nothing from this stage reaches the final image except the installed
# packages themselves — no build tools, no apt cache, no pip cache.
#
# Why multi-stage?
#   build-essential (~200 MB) and curl are only needed during pip install.
#   Keeping them out of the final image shrinks it and removes tools an
#   attacker could use if they ever gained code execution inside the container.
# =============================================================================

FROM python:3.11-slim AS builder

# Prevent .pyc files and enable unbuffered stdout/stderr in the build stage
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Tell pip to install into /install so we can COPY just that directory
    PIP_PREFIX=/install \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/install/lib/python3.11/site-packages"

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# =============================================================================
# Stage 2 — runtime
# =============================================================================
# A clean image that contains only what the app needs to run.
# =============================================================================

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/install/lib/python3.11/site-packages" \
    PATH="/install/bin:$PATH"

# ---------------------------------------------------------------------------
# Non-root user
# ---------------------------------------------------------------------------
# By default Docker runs as root (UID 0). If an attacker exploits a
# vulnerability in the app or one of its dependencies, they land as root
# inside the container — which makes escaping to the host much easier.
#
# Creating a dedicated user means:
#   - The process runs as UID 1000 with no special privileges.
#   - Files written by the app (data/, storage/, query_logs.csv) are owned
#     by appuser, not root.
#   - The home directory /home/appuser is writable; everything else is not.
#
# --no-create-home is intentionally NOT used here: Streamlit and some
# Python libraries write to ~/.streamlit or ~/.cache and will fail
# silently or loudly without a writable home directory.
# ---------------------------------------------------------------------------

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --create-home appuser

# Copy installed packages from the builder stage
COPY --from=builder /install /install

# Copy application source — owned by appuser from the start.
# Using --chown here (rather than a separate RUN chown) avoids creating an
# extra layer and is faster because chown is applied during the COPY itself.
WORKDIR /app
COPY --chown=appuser:appuser . .

# Create the runtime directories the app will write to.
# Must happen before USER so we have root permission to create them,
# then hand ownership to appuser.
RUN mkdir -p data storage \
    && chown -R appuser:appuser data storage

# ---------------------------------------------------------------------------
# Drop privileges — all subsequent RUN, CMD, ENTRYPOINT run as appuser
# ---------------------------------------------------------------------------
USER appuser

# Streamlit listens on 8501
EXPOSE 8501

# Healthcheck uses curl (present in the slim base) against Streamlit's
# built-in health endpoint. failure threshold = 3 gives the app up to
# 30 s (3 × 10 s interval) to start before the container is marked unhealthy.
HEALTHCHECK \
    --interval=10s \
    --timeout=5s \
    --start-period=30s \
    --retries=3 \
    CMD curl --silent --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true"]
