# traceability-bot
A chatbot that provides easy and fast answers to requirements-to-code traceability related questions.

Built for a Bachelors Project of Computing Science at RUG.

## How to run

After correctly pip installing the requirements.txt no other dependency issues should occur.

### Local
cd backend\
pip install -r requirements.txt\
mkdir debug\
python manage.py runserver localhost:8000

cd frontend\
python -m http.server 8080

### Containerized
docker compose up --build

(When running the application dockerized similarity graphs dont show yet)
