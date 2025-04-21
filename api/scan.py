from flask import Blueprint, jsonify
from flask_httpauth import HTTPTokenAuth
import subprocess

from api.auth import token_auth  # dein bestehendes Auth-System

scan = Blueprint('scan', __name__)
auth = HTTPTokenAuth(scheme='Bearer')

@scan.route('/scan', methods=['POST'])
@token_auth.login_required
def perform_scan():
    try:
        result = subprocess.run(
            ['whoami'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        output = result.stdout.decode().strip()
        return jsonify({"user": output})
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Subprocess failed",
            "stdout": e.stdout.decode() if e.stdout else "",
            "stderr": e.stderr.decode() if e.stderr else "",
            "exit_code": e.returncode
        }), 500
