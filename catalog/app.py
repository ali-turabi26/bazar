from flask import Flask, jsonify
import sqlite3, os

app = Flask(__name__)
DB_PATH = os.getenv("DB_PATH", "/data/catalog.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("/data", exist_ok=True)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            topic TEXT,
            quantity INTEGER,
            price REAL
        )
    """)
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM books")
    if cur.fetchone()[0] == 0:
        books = [
            ("How to get a good grade in DOS in 40 minutes a day", "distributed systems", 5, 10.0),
            ("RPCs for Noobs", "distributed systems", 5, 50.0),
            ("Xen and the Art of Surviving Undergraduate School", "undergraduate school", 5, 10.0),
            ("Cooking for the Impatient Undergrad", "undergraduate school", 5, 20.0),
        ]
        cur.executemany("INSERT INTO books (title, topic, quantity, price) VALUES (?, ?, ?, ?)", books)
        conn.commit()
    conn.close()

@app.get("/search/<topic>")
def search(topic):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books WHERE topic LIKE ?", (topic,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.get("/info/<int:book_id>")
def info(book_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books WHERE id=?", (book_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"error": "Book not found"}), 404

@app.post("/update/<int:book_id>")
def update(book_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id=? AND quantity > 0", (book_id,))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        return jsonify({"error": "Book out of stock"}), 400
    conn.close()
    return jsonify({"status": "success"})

# Auto-create DB every time
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
