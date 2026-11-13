FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt \
    && useradd --create-home --uid 10001 appuser

COPY app.py ./
COPY templates ./templates
COPY static ./static

USER appuser
EXPOSE 10000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --access-logfile - --error-logfile - app:app"]
