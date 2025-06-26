# traceability-bot
A chatbot that provides easy and fast answers to requirements-to-code tracing related questions

## How to run

### Local
cd backend
pip install -r requirements.txt
mkdir debug
python manage.py runserver localhost:8000

cd frontend
python3 -m http.server 8080

### Containerized
docker compose up --build
