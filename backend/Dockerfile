FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

WORKDIR /app
RUN mkdir -p debug

CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]
