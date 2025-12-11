FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends tzdata && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/python/app.py ./src/python/app.py

EXPOSE 5000

WORKDIR /app/src/python
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]