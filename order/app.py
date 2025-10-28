from flask import Flask, jsonify
import requests, csv

app = Flask(__name__)

CATALOG_URL = "http://catalog:5001"
ORDERS_FILE = "orders.csv"

def log_order(item_id, title):
    with open(ORDERS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([item_id, title])

@app.route('/purchase/<int:item_id>', methods=['POST'])
def purchase(item_id):
    # Check stock
    r = requests.get(f"{CATALOG_URL}/query/item/{item_id}")
    if r.status_code != 200:
        return jsonify({"error": "Item not found"}), 404

    item = r.json()
    if item["quantity"] <= 0:
        return jsonify({"error": "Out of stock"}), 400

    # Decrement stock
    new_q = item["quantity"] - 1
    requests.put(f"{CATALOG_URL}/update/{item_id}", json={"quantity": new_q})
    log_order(item_id, item["title"])
    return jsonify({"message": f"bought book {item['title']}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
