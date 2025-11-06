from flask import Flask, jsonify, request, abort
import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "catalog.db")

app = Flask(__name__)

def db():
    return sqlite3.connect(DB_PATH)

def init_db():
    con = db()
    cur = con.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        topic TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL
      )
    """)
    con.commit()
    # Seed if empty
    cur.execute("SELECT COUNT(*) FROM books")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO books(id,title,topic,quantity,price) VALUES(?,?,?,?,?)",
            [
                (1, "How to get a good grade in DOS in 40 minutes a day", "distributed systems", 5, 10.0),
                (2, "RPCs for Noobs", "distributed systems", 5, 50.0),
                (3, "Xen and the Art of Surviving Undergraduate School", "undergraduate school", 5, 30.0),
                (4, "Cooking for the Impatient Undergrad", "undergraduate school", 5, 20.0),
            ],
        )
        con.commit()
    con.close()

@app.get("/search/<topic>")
def search(topic):
    con = db(); cur = con.cursor()
    cur.execute("SELECT id,title FROM books WHERE topic = ?", (topic,))
    rows = [{"id": r[0], "title": r[1]} for r in cur.fetchall()]
    con.close()
    return jsonify(rows)

@app.get("/info/<int:item_id>")
def info(item_id):
    con = db(); cur = con.cursor()
    cur.execute("SELECT title,quantity,price FROM books WHERE id = ?", (item_id,))
    r = cur.fetchone()
    con.close()
    if not r: abort(404)
    return jsonify({"title": r[0], "quantity": r[1], "price": r[2]})

@app.put("/update/<int:item_id>")
def update(item_id):
    data = request.get_json(force=True, silent=True) or {}
    delta = data.get("delta_quantity")  # e.g., -1 for purchase
    price = data.get("price")
    con = db(); cur = con.cursor()
    cur.execute("SELECT quantity FROM books WHERE id = ?", (item_id,))
    row = cur.fetchone()
    if not row:
        con.close(); abort(404)
    quantity = row[0]
    if delta is not None:
        new_q = quantity + int(delta)
        if new_q < 0:
            con.close(); return jsonify({"error": "insufficient stock"}), 409
        cur.execute("UPDATE books SET quantity=? WHERE id=?", (new_q, item_id))
    if price is not None:
        cur.execute("UPDATE books SET price=? WHERE id=?", (float(price), item_id))
    con.commit(); con.close()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
