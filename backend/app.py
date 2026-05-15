# flask is a micro web framework
from flask import Flask, request, jsonify
from flask_cors import CORS
# None of the inventory logic occurs here it just imports the service and function. 
from inventory_service import (
    get_all_inventories,
    add_record,
    query_quantity,
    delete_record
)

# This creates the flask server CORS(app) allow the backend to accept frontend request.
app = Flask(__name__)
CORS(app)

# This creates a route called GET/inventories
@app.route("/inventories", methods=["GET"])
def inventories():
    return jsonify(get_all_inventories())

# The add record route.
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

# This is used when the frontend wants to search for an item quantity.
@app.route("/query", methods=["POST"])
def query():
    data = request.json
    result = query_quantity(data["item_id"])
    return jsonify(result)

# This helps in the process of deletion as it receives an item ID and deletes that record from all inventory nodes.
@app.route("/delete-record", methods=["POST"])
def delete():
    data = request.json
    result = delete_record(data["item_id"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)