# PostgreSQL deployment

This Flask application requires PostgreSQL. `DATABASE_URL` is mandatory; SQLite is rejected at startup.

On Render, create a **PostgreSQL** database in the same region as the Web Service. Copy its **Internal Database URL** into the Web Service environment variable `DATABASE_URL`. Also set `SECRET_KEY` and `ADMIN_SETUP_KEY`.

The application calls `db.create_all()` on startup, so a new empty database is initialized automatically. No old SQLite data is migrated. To initialize manually, run:

```bash
DATABASE_URL="postgresql://..." python -c "from app import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"
```

Use a Render start command such as `gunicorn app:app`.
