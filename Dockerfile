FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN useradd --create-home --uid 1000 app \
    && mkdir -p /app/data/corpus \
    && chown -R app:app /app

COPY --chown=app:app . .
USER app

CMD ["python", "-m", "unittest", "discover", "-v"]
