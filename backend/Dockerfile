FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt



COPY . /app
WORKDIR /app

RUN python build-parsers.py

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
