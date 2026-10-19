# PostgreSQL deployment

This Flask application requires PostgreSQL. `DATABASE_URL` is mandatory; SQLite is rejected at startup.

On Render, create a **PostgreSQL** database in the same region as the Web Service. Copy its **Internal Database URL** into the Web Service environment variable `DATABASE_URL`. Set `SECRET_KEY` to a randomly generated string of at least 32 characters, set a separate random `ADMIN_SETUP_KEY`, and set `ENCRYPTION_KEY` to a persistent Fernet key generated with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Never use the example placeholders or commit actual credentials. Keep these values unchanged across redeploys; changing `ENCRYPTION_KEY` loses access to previously saved provider keys. When upgrading a database containing legacy API keys, retain its original `ENCRYPTION_SALT` (the old default was `my-app-salt`); startup converts legacy credentials to Fernet encryption.

The application calls `db.create_all()` and its idempotent PostgreSQL schema migrations on startup, so a new empty database is initialized automatically and an existing database receives newly added columns. No old SQLite data is migrated. To initialize manually, run:

```bash
DATABASE_URL="postgresql://..." python -c "from app import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"
```

Use a Render start command such as `gunicorn --workers 1 --bind 0.0.0.0:$PORT app:app`. Run behind HTTPS, set `TRUST_PROXY=1` only when the app is behind Render's trusted TLS-terminating proxy (for HTTPS canonical links and HSTS), and leave `FLASK_ENV` unset in production so session cookies are marked Secure. Do not run the built-in Flask development server for public deployment.

After deployment, open `/health`. A successful application and database connection returns `{"status":"ok"}`. Unhandled application exceptions are also written to the service logs with their traceback.

Before going live, configure optional provider credentials (`DEEPSEEK_API_KEY`, `MANGOOLS_API_KEY`) in your host's secret manager, verify admin setup and login, trial checkout, and the phone link on a mobile device. The former homepage contact form was a nonfunctional mock; contact is now by phone. Back up PostgreSQL regularly and restrict database access to the application. For older deployments that used the predictable Flask secret or stored API credentials with reversible Base64, rotate the Flask secret and any exposed provider API keys.

Public-launch follow-ups: configure persistent rate limits for login, signup, and paid external API calls (and per-user usage quotas when using the shared default API keys). The current security headers restrict framing, forms, and object embedding but do not enforce a strict `script-src` because the existing templates contain inline JavaScript and third-party CDN assets. If stronger XSS isolation is required, move inline scripts into local files and deploy a restrictive CSP. Verify these changes against a staging PostgreSQL instance before directing live traffic; local syntax checks cannot validate the live database migration or provider integrations.
