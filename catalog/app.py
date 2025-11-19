from flask import Flask, jsonify
import sqlite3, os

app = Flask(__name__)

# SQLite DB path – in Docker this will be /data/catalog.db
DB_PATH = os.getenv("DB_PATH", "/data/catalog.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Make sure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)

    conn.commit()

    # Seed initial 4 books if table is empty
    cur.execute("SELECT COUNT(*) FROM books")
    if cur.fetchone()[0] == 0:
        books = [
            ("How to get a good grade in DOS in 40 minutes a day", "distributed systems", 5, 10.0),
            ("RPCs for Noobs", "distributed systems", 5, 50.0),
            ("Xen and the Art of Surviving Undergraduate School", "undergraduate school", 5, 10.0),
            ("Cooking for the Impatient Undergrad", "undergraduate school", 5, 20.0),
        ]
        cur.executemany(
            "INSERT INTO books (title, topic, quantity, price) VALUES (?, ?, ?, ?)",
            books
        )
        conn.commit()

    conn.close()


@app.get("/search/<topic>")
def search(topic):
    conn = get_db()
    cur = conn.cursor()
    # exact match on topic (works for "distributed systems" etc.)
    cur.execute("SELECT id, title FROM books WHERE topic = ?", (topic,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.get("/info/<int:book_id>")
def info(book_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, topic, quantity, price FROM books WHERE id = ?", (book_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"error": "Book not found"}), 404


@app.post("/update/<int:book_id>")
def update(book_id):
    conn = get_db()
    cur = conn.cursor()
    # Decrement stock if > 0
    cur.execute(
        "UPDATE books SET quantity = quantity - 1 WHERE id = ? AND quantity > 0",
        (book_id,)
    )
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        return jsonify({"error": "Book out of stock"}), 400
    conn.close()
    return jsonify({"status": "success"})


# Create DB and seed data when container starts
init_db()

if __name__ == "__main__":
    # 5000 is internal container port – we map from host using docker-compose
    app.run(host="0.0.0.0", port=5000)
