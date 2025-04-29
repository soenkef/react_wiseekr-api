#!/bin/sh

echo "⏳ Warte auf die Docker Datenbank (db:3306)..."
./wait-for-it.sh db:3306 --timeout=60 --strict -- echo "✅ Datenbank ist bereit."

# Flask-Umgebung
export FLASK_APP=api.app:create_app
export FLASK_ENV=development

# Nur wenn keine Migration existiert
#if [ ! "$(ls -A migrations/versions 2>/dev/null)" ]; then
#  echo "⚙️  Erzeuge initiale Migration..."
#  flask db migrate -m "Initial"
#fi
flask db init
flask db migrate -m "Autogen" || true

echo "📦 Führe Migration aus..."
flask db stamp head
flask db migrate -m "Initial"
flask db upgrade

echo "🚀 Starte Gunicorn..."
exec gunicorn -b :5000 --timeout 600 --access-logfile - --error-logfile - wiseekr:app