# PhotoShare Cloud — Backend

Django 5.1 API for PhotoShare Cloud. Apps: `accounts`, `media_posts`, `comments`, `ratings`, `analytics`.

## Requirements

- Python 3.11+ (project uses 3.11 in local setups)
- Dependencies in `requirements.txt` (Django REST Framework, JWT, CORS, Pillow, optional PostgreSQL via `psycopg2-binary`, Redis and Celery for async work)

## Setup

1. Create and activate a virtual environment (from this directory):

   ```bash
   python3 -m venv env
   source env/bin/activate   # Windows: env\Scripts\activate
   ```

2. Install packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations and create a superuser (optional):

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Run the development server:

   ```bash
   python manage.py runserver
   ```

   Admin is at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## Configuration

- Default database in `config/settings.py` is SQLite (`db.sqlite3` in the project root). For PostgreSQL, point `DATABASES` at your instance and keep credentials out of git (for example with `python-decouple` and a `.env` file).
- For production, set `DEBUG = False`, configure `ALLOWED_HOSTS`, and use a strong `SECRET_KEY` from the environment — never commit real secrets.

## Celery and Redis

`redis` and `celery` are listed for background tasks. Wire them in `settings` and run a worker when those features are enabled.
