from flask import Blueprint, jsonify, current_app
from api.app import db
from api.models import Settings

settings_bp = Blueprint('settings_bp', __name__)

@settings_bp.route('/settings', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_settings():
    # Wir erwarten genau einen Settings-Eintrag
    settings = db.session.query(Settings).first()
    if not settings:
        return jsonify({'error': 'Settings nicht gefunden'}), 404
    return jsonify({'is_active': settings.is_active}), 200