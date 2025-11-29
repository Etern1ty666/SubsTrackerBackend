# SubsTrackerBackend

1. download postgresql https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

2. создать для django бд:

psql -U postgres

CREATE USER django_admin WITH PASSWORD '123';

CREATE DATABASE django OWNER django_admin;

GRANT ALL PRIVILEGES ON DATABASE django TO django_admin;


3. download and start redis-server.exe https://github.com/tporadowski/redis/releases

4. Подставить в .env tg bot token
   
6. создать venv и активировать

pip install -r requirements.txt

6. 
python manage.py migrate

python manage.py runserver

7. 
в другом терминале

активировать тот же самый venv

celery -A backend worker --loglevel=info
