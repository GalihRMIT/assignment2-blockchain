from flask import Flask, request, jsonify
from flask_cors import CORS
from inventory_service import (
    get_all_inventories,
    add_record,
    query_quantity,
    delete_record
)

app = Flask(__name__)
CORS(app)

@app.route("/inventories", methods=["GET"])
def inventories():
    return jsonify(get_all_inventories())

@app.route("/add-record", methods=["POST"])
def add_new_record():
    data = request.json

    result = add_record(
        item_id=data["item_id"],
        quantity=int(data["quantity"]),
        price=int(data["price"]),
        location=data["location"],
        signer=data["signer"]
    )

    return jsonify(result)

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    result = query_quantity(data["item_id"])
    return jsonify(result)

@app.route("/delete-record", methods=["POST"])
def delete():
    data = request.json
    result = delete_record(data["item_id"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)