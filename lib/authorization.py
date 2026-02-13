import os
import secrets
from flask import request, jsonify
from lib import config
from lib import postgres 

class Authorization:
    def __init__(self):

        self.MASTER_KEY = config.get("app")['masterkey']

    def require(self):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer: "):
            return jsonify({"status": "error", "message": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        db = postgres.init()
        query = "SELECT * FROM api_tokens WHERE token = %s AND active = TRUE"
        rows = db.select(query, (token,))

        if len(rows) == 1:
            db.update("UPDATE api_tokens SET last_used = NOW() WHERE token = %s", (token,))

        db.close()

        if len(rows) == 0:
            return jsonify({"status": "error", "message": "Invalid or inactive token"}), 403

        return None
    
    def create(self):
        master = request.headers.get("X-Master-Key")
        if master != self.MASTER_KEY:
            return jsonify({"status": "error", "message": "Unauthorized"}), 403

        data = request.get_json(silent=True) or {}
        description = data.get("description", "API token")

        token = secrets.token_hex(32)

        db = postgres.init()
        db.insert(
            "INSERT INTO api_tokens (token, description, active) VALUES (%s, %s, TRUE)",
            (token, description)
        )
        db.close()

        return jsonify({"status": "ok", "token": token})

    def revoke(self):
        check = self.require()
        if check:
            return check

        data = request.get_json()
        token_to_revoke = data.get("token")

        if not token_to_revoke:
            return jsonify({"status": "error", "message": "Token required"}), 400

        db = postgres.init()
        db.update("UPDATE api_tokens SET active = FALSE WHERE token = %s", (token_to_revoke,))
        db.close()

        return jsonify({"status": "ok", "message": "Token revoked"})
