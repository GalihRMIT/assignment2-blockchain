import json
from key_store import Inventory_Keys
from crypto_utils import hash_record, rsa_sign, rsa_verify

# This is where the main Backend Logic Lies controling the systems logic
# Loading Invnetory, Saving Inventory data, adding new signed records, checking the agreement across nodes (you get the idea)

# This is the Inventory file mapping where all the Inventory files are located
Inventory_Files = {
    "Inventory A": "data/inventory_A.json",
    "Inventory B": "data/inventory_B.json",
    "Inventory C": "data/inventory_C.json",
    "Inventory D": "data/inventory_D.json"
}

# This just opens up the JSON file and loads the inventory record to python. 
def load_inventory(filename):
    with open(filename, "r") as file:
        return json.load(file)

# Similarly this function writes updated to the inventory back into the JSON file
def save_inventory(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# This function just loops through all of the inventories. Returning them as one big dictionary. 
def get_all_inventories():
    inventories = {}

    for node_name, filename in Inventory_Files.items():
        inventories[node_name] = load_inventory(filename)

    return inventories

# 3 phase PBFT 
def validate_record_node (node_name, filename, record, signature, signer_keys, hash_int):
    node_result = {
        "signature_check": None,
        "duplicate_check": None,
        "decision": None
    }

    recovered_hash = rsa_verify(signature, signer_keys["e"], signer_keys["n"])

    if recovered_hash == hash_int:
        node_result["signature_check"] = "VALID"
    else:
        node_result["signature_check"] = "INVALID"

    inventory_data = load_inventory(filename)

    duplicate_found = False

    for item in inventory_data:
        if str (item["item_id"]).strip() == str(record["item_id"]).strip():
            duplicate_found = True
            break

    if duplicate_found:
        node_result["duplicate_check"] = "DUPLICATE FOUND"
    else:
        node_result["duplicate_check"] = "NO DUPLICATE"

    if node_result["signature_check"] == "VALID" and node_result["duplicate_check"] == "NO DUPLICATE":
        node_result["decision"] = "ACCEPT"
    else:
        node_result["decision"] = "REJECT"

    return node_result

def run_pbft_consensus(record, signature, signer_keys, hash_int):
    pbft_results = {
        "pre_prepare_phase": {},
        "prepare_phase": {},
        "commit_phase": {}
    }

    # The first Phase: Pre Prepare
    pbft_results["pre_prepare_phase"] = {
        "proposal": "Signed record proposed by submitting inventory node",
        "record": record,
        "signature": signature
    }

    # The Second Phase: Prepare 
    accept_count = 0
    reject_count = 0

    for node_name, filename in Inventory_Files.items():
        node_result = validate_record_node(
            node_name=node_name,
            filename=filename,
            record=record,
            signature=signature,
            signer_keys=signer_keys,
            hash_int=hash_int
        )

        pbft_results["prepare_phase"][node_name] = node_result

        if node_result["decision"] == "ACCEPT":
            accept_count += 1
        else :
            reject_count += 1
        
    # The Third Phase: commit
    total_nodes = len(Inventory_Files)
    required_accepts = 3  # This shows that for the 4 nodes the PBFT requires 3 out of 4 agreement

    consensus_passed = accept_count >= required_accepts

    pbft_results["commit_phase"] = {
        "total_nodes": total_nodes,
        "required_accepts": required_accepts,
        "accept_count": accept_count,
        "reject_count": reject_count,
        "consensus_result": "ACCEPTED" if consensus_passed else "REJECTED"
    }

    return consensus_passed,pbft_results




# Self explaniroty function it adds a new record 
def add_record(item_id, quantity, price, location, signer):
    # just makes the input clean a -> A 
    signer = signer.upper().strip()
    location = location.upper().strip()

    # Checks if the submitting node has a valid RSA key 
    # So that only A, B, C, and D can submit records.
    if signer not in Inventory_Keys:
        return {
            "success": False,
            "message": "Invalid Inventory node. Record rejected."
        }
    # just creates the the inventory record as python dictionary 
    new_record = {
        "item_id": item_id,
        "quantity": quantity,
        "price": price,
        "location": location
    }

    # If the singer of the message is A then it takes the key for Inventory A 
    signer_keys = Inventory_Keys[signer]

    # This just transforms the inventory record into a hash 
    hash_hex, hash_int = hash_record(new_record)

    # This creates the RSA digital signiture and proves that the record was signed by the inventroy node that owns the private key d
    signature = rsa_sign(hash_int, signer_keys["d"], signer_keys["n"])

    # This will run the simplified PBFT consensus
    consensus_passed, pbft_results = run_pbft_consensus(
        record=new_record,
        signature=signature,
        signer_keys=signer_keys,
        hash_int=hash_int
    )

    # If it fails the PBFT consensus will not store the recrod 
    if not consensus_passed:
        return {
            "success": False,
            "message": "PBFT consensus failed. Record rejected Uhoh.",
            "record": new_record,
            "submitting_node": f"Inventory {signer}",
            "hash_hex": hash_hex,
            "hash_int": hash_int,
            "signature": signature,
            "pbft_results": pbft_results,
            "consensus_result": "REJECTED"
        }
    
    # If all of the verification result are valid then the record gets added to every JSON inventory file
    for filename in Inventory_Files.values():
        inventory_data = load_inventory(filename)
        inventory_data.append(new_record)
        save_inventory(filename, inventory_data)

    # This just returns all of the impoortant value back to the UI
    return {
        "success": True,
        "message": "Record accepted and stored across all inventory nodes.",
        "record": new_record,
        "submitting_node": f"Inventory {signer}",
        "hash_hex": hash_hex,
        "hash_int": hash_int,
        "signature": signature,
         "pbft_results": pbft_results,
        "consensus_result": "ACCEPTED"
    }

# NOTE Currently Louis Placeholder :)
def query_quantity(item_id):
    results = {}

    # Just checks each JSON file for the ITEM ID 
    # If they find it then it stores the quantity. If not it stores none
    for node_name, filename in Inventory_Files.items():
        inventory_data = load_inventory(filename)

        found_quantity = None

        for item in inventory_data:
            if str(item["item_id"]).strip() == str(item_id).strip():
                found_quantity = item["quantity"]
                break

        results[node_name] = found_quantity

    # This creates a list of only the quantities that were actually found.
    valid_results = [q for q in results.values() if q is not None]

    # If nobody has the item it returns no result
    if len(valid_results) == 0:
        return {
            "success": False,
            "message": "Item does not exist in the inventory system.",
            "query_results": results,
            "consensus_result": "NO RESULT"
        }

    #This check if 1st all quantities are the same 2nd if all 4 nodes had the item
    if len(set(valid_results)) == 1 and len(valid_results) == len(Inventory_Files):
        return {
            "success": True,
            "message": "All inventory nodes agree.",
            "query_results": results,
            "final_quantity": valid_results[0],
            "consensus_result": "AGREED"
        }

    # If the nodes disagree then the system will not trust the result
    return {
        "success": False,
        "message": "Inventory nodes do not agree. Query result cannot be trusted.",
        "query_results": results,
        "consensus_result": "FAILED"
    }

# Removes an item from all the nodes 
def delete_record(item_id):
    found = False

    # The main Delete loop
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