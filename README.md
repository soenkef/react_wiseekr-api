# wiseekr-api

[![Build status](https://github.com/miguelgrinberg/wiseekr-api/workflows/build/badge.svg)](https://github.com/miguelgrinberg/wiseekr-api/actions) [![codecov](https://codecov.io/gh/miguelgrinberg/wiseekr-api/branch/main/graph/badge.svg)](https://codecov.io/gh/miguelgrinberg/wiseekr-api)

A modern (as of 2024) Flask API back end.

## Deploy to Heroku

Click the button below to deploy the application directly to your Heroku
account.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/miguelgrinberg/wiseekr-api/tree/heroku)

## Deploy on your Computer

### Setup

Follow these steps if you want to run this application on your computer, either
in a Docker container or as a standalone Python application.

```bash
git clone https://github.com/miguelgrinberg/wiseekr-api
cd wiseekr-api
cp .env.example .env
```

Open the new `.env` file and enter values for the configuration variables.

### Run with Docker

To start:

```bash
docker-compose up -d
```

The application runs on port 5000 on your Docker host. You can access the API
documentation on the `/docs` URL (i.e. `http://localhost:5000/docs` if you are
running Docker locally).

To populate the database with some randomly generated data:

```bash
docker-compose run --rm wiseekr-api bash -c "flask fake users 10 && flask fake posts 100"
```

To stop the application:

```bash
docker-compose down
```

### Run locally

Set up a Python 3 virtualenv and install the dependencies on it:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the database and populate it with some randomly generated data:

```bash
alembic upgrade head
flask fake users 10
flask fake posts 100
```

Run the application with the Flask development web server:

```bash
flask run
```

The application runs on `localhost:5000`. You can access the API documentation
at `http://localhost:5000/docs`.

## Troubleshooting

On macOS Monterey and newer, Apple decided to use port 5000 for its AirPlay
service, which means that the wiseekr API server will not be able to run on
this port. There are two possible ways to solve this problem:

1. Disable the AirPlay Receiver service. To do this, open the System
Preferences, go to "Sharing" and uncheck "AirPlay Receiver".
2. Move wiseekr API to another port:
    - If you are running wiseekr API with Docker, add a
    `wiseekr_API_PORT=4000` line to your *.env* file. Change the 4000 to your
    desired port number.
    - If you are running wiseekr API with Python, start the server with the
    command `flask run --port=4000`.
# react_wiseekr-api

# Updated Database
## create manage.py in root
from flask.cli import FlaskGroup
from api.app import create_app, db
from flask_migrate import MigrateCommand

app = create_app()
cli = FlaskGroup(app)

### Migrate-Befehle hinzufügen
cli.add_command('db', MigrateCommand)

if __name__ == '__main__':
    cli()

## export Environment variables
export FLASK_APP=app:create_app
export FLASK_ENV=development

## remove migrations folder
rm -rf migrations/

## eventually must remove alembic_version table from database table
DROP TABLE alembic_version;

## reinit and build database
flask db init
flask db migrate -m "initial schema after reset"
flask db upgrade

### if database already exists
rm -r migrations/
flask db init
flask db stamp head
flask db migrate -m "initial schema after reset"
flask db upgrade

# REACT WISEEKR
## https://github.com/soenkef/react_wiseekr

