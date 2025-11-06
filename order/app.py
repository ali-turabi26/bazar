from flask import Flask, jsonify
import os, sqlite3, requests

CATALOG_URL = os.environ.get("CATALOG_URL", "http://catalog:5000")
DB_PATH = os.environ.get("ORDERS_DB", "orders.db")

app = Flask(__name__)

def db():
    return sqlite3.connect(DB_PATH)

def init_db():
    con = db(); cur = con.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        title TEXT NOT NULL
      )
    """)
    con.commit(); con.close()

@app.post("/purchase/<int:item_id>")
def purchase(item_id):
    # 1) check stock
    r = requests.get(f"{CATALOG_URL}/info/{item_id}", timeout=3)
    if r.status_code != 200:
        return jsonify({"status": "error", "message": "item not found"}), 404
    info = r.json()
    if info["quantity"] <= 0:
        return jsonify({"status": "fail", "message": "out of stock"}), 409
    # 2) decrement stock
    u = requests.put(f"{CATALOG_URL}/update/{item_id}", json={"delta_quantity": -1}, timeout=3)
    if u.status_code != 200:
        return jsonify({"status": "fail", "message": "could not update stock"}), 409
    # 3) log order
    con = db(); cur = con.cursor()
    cur.execute("INSERT INTO orders(item_id,title) VALUES(?,?)", (item_id, info["title"]))
    con.commit(); con.close()
    return jsonify({"status":"success","message":f"bought book {info['title']}"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
