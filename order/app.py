from flask import Flask, jsonify
import sqlite3, os, requests

app = Flask(__name__)

# Where catalog service lives inside Docker network
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:5000")

# SQLite file for orders
ORDERS_DB = os.getenv("ORDERS_DB", "/data/orders.db")


def get_db():
    conn = sqlite3.connect(ORDERS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(ORDERS_DB), exist_ok=True)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            title TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.post("/purchase/<int:item_id>")
def purchase(item_id):
    try:
        # Get info about the book from catalog
        r = requests.get(f"{CATALOG_URL}/info/{item_id}", timeout=5)
        if r.status_code != 200:
            return jsonify({"error": "Item not found"}), 404
        item = r.json()

        # Ask catalog to decrement stock
        res = requests.post(f"{CATALOG_URL}/update/{item_id}", timeout=5)
        if res.status_code != 200:
            return jsonify({"error": "Item out of stock"}), 400

        # Log order in local DB
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (item_id, title) VALUES (?, ?)",
            (item_id, item["title"])
        )
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "item": item}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
