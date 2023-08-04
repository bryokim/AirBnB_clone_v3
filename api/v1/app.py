#!/usr/bin/python3
"""Flask application"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

from models import storage
from api.v1.views import app_views

app = Flask(__name__)
CORS(app, origins="0.0.0.0")

app.register_blueprint(app_views)


@app.errorhandler(404)
def not_found(error):
    """Handle a 404 error.

    Args:
        error (obj): Error object.
    """
    return jsonify({"error": "Not found"}), 404


# @app.errorhandler(400)
# def bad_request(error):
#     """Handle 400 error.

#     Args:
#         error (obj): Error object.
#     """
#     return jsonify({"error": error.description}), 400


@app.teardown_appcontext
def close_db(expception):
    storage.close()


if __name__ == "__main__":
    host = os.getenv("HBNB_API_HOST") or "0.0.0.0"
    port = os.getenv("HBNB_API_PORT") or 5000
    app.run(host=host, port=port, threaded=True)
