FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libxml2-dev libxslt1-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install early for layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything including fallacies.csv
COPY . /app

ENV PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE 8000

RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["gunicorn", "-w", "2", "-k", "gthread", "-b", "0.0.0.0:8000", "app:app"]
