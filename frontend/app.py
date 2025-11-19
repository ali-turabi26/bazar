from flask import Flask, jsonify
import os, requests

app = Flask(__name__)

CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:5000")
ORDER_URL = os.getenv("ORDER_URL", "http://order:5000")


@app.get("/search/<topic>")
def search(topic):
    r = requests.get(f"{CATALOG_URL}/search/{topic}", timeout=5)
    return jsonify(r.json()), r.status_code


@app.get("/info/<int:book_id>")
def info(book_id):
    r = requests.get(f"{CATALOG_URL}/info/{book_id}", timeout=5)
    return jsonify(r.json()), r.status_code


@app.post("/purchase/<int:book_id>")
def purchase(book_id):
    r = requests.post(f"{ORDER_URL}/purchase/{book_id}", timeout=5)
    data = r.json()

    # REQUIRED BY HOMEWORK: print "bought book <book_name>"
    if r.status_code == 200 and data.get("status") == "success":
        title = data.get("item", {}).get("title", "UNKNOWN")
        print(f"bought book {title}")

    return jsonify(data), r.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
