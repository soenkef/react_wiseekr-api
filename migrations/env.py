from logging.config import fileConfig
from alembic import context
from flask import current_app
import logging

from api.app import create_app, db
from config import Config

# Konfiguration & Logging
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Flask-App & DB vorbereiten
app = create_app(Config)

# Nur Kontext betreten, wenn nötig
def run_migrations_online():
    with app.app_context():
        connectable = db.get_engine()
        target_metadata = db.Model.metadata

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()

def run_migrations_offline():
    with app.app_context():
        connectable = db.get_engine()
        target_metadata = db.Model.metadata

        url = str(connectable.url).replace('%', '%%')
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# Entscheide je nach Modus
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
