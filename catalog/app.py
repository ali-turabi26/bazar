from flask import Flask, request, jsonify
import csv

app = Flask(__name__)

CATALOG_FILE = "catalog.csv"

def read_catalog():
    with open(CATALOG_FILE, newline='') as f:
        return list(csv.DictReader(f))

def write_catalog(data):
    with open(CATALOG_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id","title","topic","price","quantity"])
        writer.writeheader()
        writer.writerows(data)

@app.route('/query/topic/<topic>', methods=['GET'])
def query_by_topic(topic):
    data = read_catalog()
    result = [ {"id": b["id"], "title": b["title"]} for b in data if b["topic"].lower() == topic.lower() ]
    return jsonify(result)

@app.route('/query/item/<int:item_id>', methods=['GET'])
def query_by_item(item_id):
    data = read_catalog()
    for b in data:
        if int(b["id"]) == item_id:
            return jsonify({"title": b["title"], "quantity": int(b["quantity"]), "price": float(b["price"])})
    return jsonify({"error": "Item not found"}), 404

@app.route('/update/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = read_catalog()
    payload = request.get_json()
    for b in data:
        if int(b["id"]) == item_id:
            b["quantity"] = payload.get("quantity", b["quantity"])
            b["price"] = payload.get("price", b["price"])
            write_catalog(data)
            return jsonify({"message": "Updated"})
    return jsonify({"error": "Item not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
