from flask import Blueprint, jsonify
from api.app import db
from sqlalchemy import text

clear_db = Blueprint('clear_db', __name__)

@clear_db.route('/clear_db', methods=['POST'])
def clear_database():
    try:
        # Reihenfolge beachten wegen Foreign Key Constraints
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

        return jsonify({"message": "Alle Tabellen erfolgreich geleert."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
