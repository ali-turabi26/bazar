from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CATALOG_URL = "http://catalog:5001"
ORDER_URL = "http://order:5002"

@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    r = requests.get(f"{CATALOG_URL}/query/topic/{topic}")
    return jsonify(r.json())

@app.route('/info/<int:item_id>', methods=['GET'])
def info(item_id):
    r = requests.get(f"{CATALOG_URL}/query/item/{item_id}")
    return jsonify(r.json())

@app.route('/purchase/<int:item_id>', methods=['POST'])
def purchase(item_id):
    r = requests.post(f"{ORDER_URL}/purchase/{item_id}")
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
