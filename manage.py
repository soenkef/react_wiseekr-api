from flask.cli import FlaskGroup
from api.app import create_app, db
from flask_migrate import MigrateCommand

app = create_app()
cli = FlaskGroup(app)

# Migrate-Befehle hinzufügen
cli.add_command('db', MigrateCommand)

if __name__ == '__main__':
    cli()
