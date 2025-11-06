from flask import Flask, jsonify
import os, requests

CATALOG_URL = os.environ.get("CATALOG_URL", "http://catalog:5000")
ORDER_URL   = os.environ.get("ORDER_URL",   "http://order:5000")

app = Flask(__name__)

@app.get("/search/<topic>")
def search(topic):
    r = requests.get(f"{CATALOG_URL}/search/{topic}", timeout=3)
    return (r.text, r.status_code, {"Content-Type":"application/json"})

@app.get("/info/<int:item_id>")
def info(item_id):
    r = requests.get(f"{CATALOG_URL}/info/{item_id}", timeout=3)
    return (r.text, r.status_code, {"Content-Type":"application/json"})

@app.post("/purchase/<int:item_id>")
def purchase(item_id):
    r = requests.post(f"{ORDER_URL}/purchase/{item_id}", timeout=5)
    return (r.text, r.status_code, {"Content-Type":"application/json"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
