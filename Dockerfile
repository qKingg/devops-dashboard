#build
FROM python:3.11-slim AS builder
WORKDIR /build
COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

#runtime
FROM python:3.11-slim
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/false appuser
WORKDIR /app
COPY --from=builder /install /usr/local

#coppy application code
COPY app/ ./app/
COPY run.py .

USER appuser

EXPOSE 5000

#dockers own health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app.main:create_app()"]