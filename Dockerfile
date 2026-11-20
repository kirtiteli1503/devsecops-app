# ---- Stage 1: build dependencies into wheels ----
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ---- Stage 2: small runtime image ----
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Run as a non-root user (Kubernetes security best practice)
RUN useradd --create-home --uid 1000 appuser
WORKDIR /home/appuser

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

COPY app ./app
USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# One worker + threads: avoids a create_all() race between workers on first boot
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "app.main:app"]
