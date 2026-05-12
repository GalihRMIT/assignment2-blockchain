import json
from key_store import Inventory_Keys
from crypto_utils import hash_record, rsa_sign, rsa_verify

Inventory_Files = {
    "Inventory A": "data/inventory_A.json",
    "Inventory B": "data/inventory_B.json",
    "Inventory C": "data/inventory_C.json",
    "Inventory D": "data/inventory_D.json"
}

def load_inventory(filename):
    with open(filename, "r") as file:
        return json.load(file)

def save_inventory(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def get_all_inventories():
    inventories = {}

    for node_name, filename in Inventory_Files.items():
        inventories[node_name] = load_inventory(filename)

    return inventories

def add_record(item_id, quantity, price, location, signer):
    signer = signer.upper().strip()
    location = location.upper().strip()

    if signer not in Inventory_Keys:
        return {
            "success": False,
            "message": "Invalid Inventory node. Record rejected."
        }

    new_record = {
        "item_id": item_id,
        "quantity": quantity,
        "price": price,
        "location": location
    }

    inventory_check = load_inventory("data/inventory_A.json")

    for item in inventory_check:
        if str(item["item_id"]) == str(item_id):
            return {
                "success": False,
                "message": "Item ID already exists. Record rejected."
            }

    signer_keys = Inventory_Keys[signer]

    hash_hex, hash_int = hash_record(new_record)
    signature = rsa_sign(hash_int, signer_keys["d"], signer_keys["n"])

    verification_results = {}

    for node in Inventory_Keys:
        if node != signer:
            recovered_hash = rsa_verify(signature, signer_keys["e"], signer_keys["n"])

            if recovered_hash == hash_int:
                verification_results[f"Inventory {node}"] = "VALID"
            else:
                verification_results[f"Inventory {node}"] = "INVALID"

    if "INVALID" in verification_results.values():
        return {
            "success": False,
            "message": "Signature verification failed. Record rejected.",
            "record": new_record,
            "hash_hex": hash_hex,
            "hash_int": hash_int,
            "signature": signature,
            "verification_results": verification_results,
            "consensus_result": "REJECTED"
        }

    for filename in Inventory_Files.values():
        inventory_data = load_inventory(filename)
        inventory_data.append(new_record)
        save_inventory(filename, inventory_data)

    return {
        "success": True,
        "message": "Record accepted and stored across all inventory nodes.",
        "record": new_record,
        "submitting_node": f"Inventory {signer}",
        "hash_hex": hash_hex,
        "hash_int": hash_int,
        "signature": signature,
        "verification_results": verification_results,
        "consensus_result": "ACCEPTED"
    }

def query_quantity(item_id):
    results = {}

    for node_name, filename in Inventory_Files.items():
        inventory_data = load_inventory(filename)

        found_quantity = None

        for item in inventory_data:
            if str(item["item_id"]).strip() == str(item_id).strip():
                found_quantity = item["quantity"]
                break

        results[node_name] = found_quantity

    valid_results = [q for q in results.values() if q is not None]

    if len(valid_results) == 0:
        return {
            "success": False,
            "message": "Item does not exist in the inventory system.",
            "query_results": results,
            "consensus_result": "NO RESULT"
        }

    if len(set(valid_results)) == 1 and len(valid_results) == len(Inventory_Files):
        return {
            "success": True,
            "message": "All inventory nodes agree.",
            "query_results": results,
            "final_quantity": valid_results[0],
            "consensus_result": "AGREED"
        }

    return {
        "success": False,
        "message": "Inventory nodes do not agree. Query result cannot be trusted.",
        "query_results": results,
        "consensus_result": "FAILED"
    }

def delete_record(item_id):
    found = False

    for node_name, filename in Inventory_Files.items():
        inventory_data = load_inventory(filename)

        updated_inventory = []

        for item in inventory_data:
            if str(item["item_id"]).strip() != str(item_id).strip():
                updated_inventory.append(item)
            else:
                found = True

        save_inventory(filename, updated_inventory)

    if found:
        return {
            "success": True,
            "message": f"Record with Item ID {item_id} deleted from all inventory nodes."
        }

    return {
        "success": False,
        "message": f"No record found with Item ID {item_id}."
    }