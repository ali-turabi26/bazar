from flask import Flask, jsonify
import os, requests

app = Flask(__name__)
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:5000")
ORDER_URL = os.getenv("ORDER_URL", "http://order:5000")

@app.get("/search/<topic>")
def search(topic):
    r = requests.get(f"{CATALOG_URL}/search/{topic}")
    return jsonify(r.json())

@app.get("/info/<int:book_id>")
def info(book_id):
    r = requests.get(f"{CATALOG_URL}/info/{book_id}")
    return jsonify(r.json())

@app.post("/purchase/<int:book_id>")
def purchase(book_id):
    r = requests.post(f"{ORDER_URL}/purchase/{book_id}")
    return jsonify(r.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
