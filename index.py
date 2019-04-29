from flask import jsonify
from app_generator import create_app

app = create_app()


@app.route("/")
def index():
    return jsonify({"message": "hi"})
