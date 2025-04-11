# Build Stage
FROM python:3.13-slim-alpine AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Production Stage
FROM python:3.13-slim-alpine
RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY --chown=appuser:appuser . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000
CMD ["gunicorn","--bind","0.0.0.0:8000","--workers","3", "Backend.wsgi:application"]
