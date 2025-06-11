FROM python:3.11-slim

WORKDIR /usr/src/app

COPY frontend/ .

EXPOSE 8080

CMD ["python", "-m", "http.server", "8080"]
