from flask.cli import FlaskGroup
from flask_migrate import Migrate, MigrateCommand
from api.app import create_app, db

app = create_app()
migrate = Migrate(app, db)

cli = FlaskGroup(app)
cli.add_command('db', MigrateCommand)

if __name__ == '__main__':
    cli()
