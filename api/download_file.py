from flask import Blueprint, send_from_directory, jsonify, current_app
from flask_cors import cross_origin
from werkzeug.utils import safe_join
from api.models import Scan  # Passe den Import an deine Projektstruktur an

# Blueprint für den Datei-Download
# Datei: download_file.py
download_file_bp = Blueprint('download_file', __name__)

@download_file_bp.route('/scans/<int:scan_id>/download', methods=['GET', 'OPTIONS'])
@cross_origin()
def download_file(scan_id):
    # Lade den Scan-Eintrag aus der Datenbank
    scan = Scan.query.get(scan_id)
    if not scan or not scan.filename:
        return jsonify({'error': 'Datei nicht gefunden'}), 404

    uploads_dir = current_app.config.get('UPLOAD_FOLDER')
    try:
        safe_join(uploads_dir, scan.filename)
    except Exception:
        return jsonify({'error': 'Ungültiger Dateipfad'}), 400

    # Sende die Datei als Attachment
    return send_from_directory(
        directory=uploads_dir,
        filename=scan.filename,
        as_attachment=True,
        attachment_filename=scan.filename
    )