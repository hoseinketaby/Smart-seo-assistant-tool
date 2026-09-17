from sqlalchemy import text

from extensions import db


POSTGRES_MIGRATIONS = (
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_started_at TIMESTAMP",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_subscribed BOOLEAN NOT NULL DEFAULT FALSE",
    "ALTER TABLE model_entries ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT FALSE",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS focus_keyword VARCHAR(160)",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS seo_title VARCHAR(70)",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS meta_description VARCHAR(320)",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS canonical_url VARCHAR(1024)",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS og_image_url VARCHAR(1024)",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS meta_robots_noindex BOOLEAN NOT NULL DEFAULT FALSE",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS meta_robots_nofollow BOOLEAN NOT NULL DEFAULT FALSE",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS seo_score INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS cover_image_alt VARCHAR(180)",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS schema_type VARCHAR(30) NOT NULL DEFAULT 'Article'",
    "ALTER TABLE site_posts ADD COLUMN IF NOT EXISTS custom_schema_json TEXT",
    "ALTER TABLE seo_settings ADD COLUMN IF NOT EXISTS custom_schema_json TEXT",
    "ALTER TABLE seo_settings ADD COLUMN IF NOT EXISTS site_logo_data BYTEA",
    "ALTER TABLE seo_settings ADD COLUMN IF NOT EXISTS site_logo_mimetype VARCHAR(64)",
    "ALTER TABLE seo_settings ADD COLUMN IF NOT EXISTS site_logo_filename VARCHAR(255)",
    "ALTER TABLE seo_settings ADD COLUMN IF NOT EXISTS site_logo_alt VARCHAR(180)",
)


def run_schema_migrations():
    if db.engine.dialect.name != "postgresql":
        return

    with db.engine.begin() as connection:
        for statement in POSTGRES_MIGRATIONS:
            connection.execute(text(statement))
