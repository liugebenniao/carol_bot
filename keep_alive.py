# keep_alive.py
from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET", "HEAD"])
def home():
    return "I'm alive", 200

def keep_alive():
    app.run(host="0.0.0.0", port=8080)
