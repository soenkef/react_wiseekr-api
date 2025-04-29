from flask import Blueprint, jsonify, current_app
from api.app import db
from sqlalchemy import text
import os, shutil
from api.scan_import import SCAN_FOLDER

clear_db = Blueprint('clear_db', __name__)

@clear_db.route('/clear_db', methods=['POST'])
def clear_database():
    try:
        # --- 1) Datenbank leeren ---
        tables = [
            "deauth_actions",
            "scan_access_points",
            "scan_stations",
            "access_points",
            "stations",
            "scans"
        ]
        for table in tables:
            db.session.execute(text(f"DELETE FROM {table}"))
        db.session.commit()

        # --- 2) Scan-Dateien löschen (mit Fehler-Handling) ---
        try:
            if os.path.isdir(SCAN_FOLDER):
                # alle Dateien und Unterordner entfernen
                shutil.rmtree(SCAN_FOLDER)
            # leeren Ordner wieder anlegen
            os.makedirs(SCAN_FOLDER, exist_ok=True)
        except Exception as fs_err:
            # nur in die Logs, nicht als 500 an den Client
            current_app.logger.warning(f"Fehler beim Löschen der Scan-Dateien: {fs_err}")

        return jsonify({"message": "Tabellen geleert & Scan-Ordner zurückgesetzt."}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Fehler beim Leeren der DB: {e}")
        return jsonify({"error": str(e)}), 500