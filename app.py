"""Small Flask app exposing puzzle endpoints and a status page.

This module provides a lightweight HTTP interface to list and attempt puzzles.
"""
from flask import Flask, jsonify, request
from core.engine import PuzzleEngine
from puzzles.registry import registry

app = Flask(__name__)
engine = PuzzleEngine(registry)


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Final-Trace Expedition 33", "puzzles": list(registry.keys())})


@app.route("/puzzle/<name>", methods=["GET"])
def get_puzzle(name):
    if name not in registry:
        return jsonify({"error": "unknown puzzle"}), 404
    meta = registry[name].describe()
    return jsonify(meta)


@app.route("/puzzle/<name>/solve", methods=["POST"])
def solve_puzzle(name):
    if name not in registry:
        return jsonify({"error": "unknown puzzle"}), 404
    payload = request.json or {}
    answer = payload.get("answer")
    try:
        ok, message = engine.attempt(name, answer)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"ok": ok, "message": message})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
