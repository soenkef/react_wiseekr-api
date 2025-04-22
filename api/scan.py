from flask import Blueprint, request, jsonify
from flask_httpauth import HTTPTokenAuth
import subprocess

from api.auth import token_auth
from apifairy import authenticate

scan = Blueprint('scan', __name__)
auth = HTTPTokenAuth(scheme='Bearer')

@scan.route('/scan', methods=['POST'])
@authenticate(token_auth)
def perform_scan():
    data = request.get_json()
    command = data.get('command', '')

    try:
        result = subprocess.run(command.split(), capture_output=True, text=True, timeout=5)
        return jsonify({"output": result.stdout.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
