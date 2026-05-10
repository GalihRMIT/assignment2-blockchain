# main.py
# Command-line interface for the Secure DLT Inventory System.
# Provides a menu to view, add, query, and delete inventory records
# across 4 distributed nodes (A, B, C, D), each backed by its own JSON file.
# All writes are RSA-signed by the submitting node and verified by the others
# before any data is stored — this is the core DLT integrity mechanism.

import json
from crypto_utils import hash_record, rsa_sign, rsa_verify
from data.Inventory_Keys import Inventory_Keys

# Maps each node label to its JSON ledger file on disk
Inventory_Files = {
    "Inventory A": "data/inventory_A.json",
    "Inventory B": "data/inventory_B.json",
    "Inventory C": "data/inventory_C.json",
    "Inventory D": "data/inventory_D.json"
}

# --- Ledger I/O helpers ---

def load_inventory(filename):
    with open(filename, "r") as file:
        return json.load(file)

def save_inventory(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# Prints all records in a single node's ledger
def show_inventory(node_name, data):
    print(f"\n--- {node_name} ---")
    for item in data:
        print(
            f"ID: {item['item_id']} | "
            f"QTY: {item['quantity']} | "
            f"Price: {item['price']} | "
            f"Loc: {item['location']} | "
        )

# Prints every node's ledger — equivalent to the Dashboard tab in the frontend
def view_all_inventories():
    for node_name, filename in Inventory_Files.items():
        inventory_data = load_inventory(filename)
        show_inventory(node_name, inventory_data)

# --- Add record with RSA signature ---

def add_new_record():
    print("\n--- Add a Brand New Inventory Record ---")

    item_id  = input("Enter The Item ID: ")
    quantity = int(input("Enter Quantity: "))
    price    = int(input("Enter The Price: "))
    location = input("Enter Location (A/B/C/D): ").upper()
    signer   = input("Which Inventory Node is submitting this Record? (A/B/C/D): ").upper().strip()

    if signer not in Inventory_Keys:
        print("\nInvalid Inventory node. Record is Rejected.")
        return

    new_record = {
        "item_id":  item_id,
        "quantity": quantity,
        "price":    price,
        "location": location
    }

    # Reject duplicate item IDs — checked against node A (all nodes are in sync)
    inventory_check = load_inventory("data/inventory_A.json")
    for item in inventory_check:
        if str(item["item_id"]) == item_id:
            print("\nError: The Item ID already exists. Record rejected.")
            return

    signer_keys = Inventory_Keys[signer]

    # Step 1 — Hash the record to produce a fixed-length integer for RSA input
    hash_hex, hash_int = hash_record(new_record)

    # Step 2 — Sign: signature = hash_int ^ d  mod  n  (uses signer's private key)
    signature = rsa_sign(hash_int, signer_keys["d"], signer_keys["n"])

    print("\n--- Digital Signature Process ---")
    print(f"Submitting Node: Inventory {signer}")
    print(f"Record Hash Hex: {hash_hex}")
    print(f"Record Hash Integer: {hash_int}")
    print(f"Digital Signature: {signature}")

    # Step 3 — Each other node verifies using the signer's public key (e, n)
    print("\n--- Signature Verification by Other Inventory Nodes ---")

    verification_result = {}
    for node in Inventory_Keys:
        if node != signer:
            # Verify: recovered = signature ^ e  mod  n  — must equal hash_int
            recovered_hash = rsa_verify(signature, signer_keys["e"], signer_keys["n"])

            if recovered_hash == hash_int:
                verification_result[node] = "VALID"
                print(f"Inventory {node} Verification: VALID")
            else:
                verification_result[node] = "INVALID"
                print(f"Inventory {node} Verification: INVALID")

    # Only write to all nodes if every verifier accepted the signature
    if "INVALID" in verification_result.values():
        print("\nFinal Signature Result: INVALID — record rejected before storage.")
        return

    print("\nFinal Signature Result: VALID")
    print("All receiving nodes verified the sender's signature.")

    for filename in Inventory_Files.values():
        inventory_data = load_inventory(filename)
        inventory_data.append(new_record)
        save_inventory(filename, inventory_data)

    print("\nNew Record added to all Inventory nodes.")
    print(
        f"ID: {new_record['item_id']} | "
        f"QTY: {new_record['quantity']} | "
        f"Price: {new_record['price']} | "
        f"Loc: {new_record['location']} | "
    )

# --- Delete a record from all nodes ---

def delete_record():
    print("\n--- Delete Inventory Record ---")

    item_id = input("Please Enter the Item ID to Delete: ").strip()
    found = False

    # Remove the matching record from every node's ledger to keep them in sync
    for _, filename in Inventory_Files.items():
        inventory_data = load_inventory(filename)

        updated_inventory = []
        for item in inventory_data:
            if str(item["item_id"]).strip() != item_id:
                updated_inventory.append(item)
            else:
                found = True

        save_inventory(filename, updated_inventory)

    if found:
        print(f"\nRecord with Item ID {item_id} deleted from all inventory nodes.")
    else:
        print(f"\nNo record found with Item ID {item_id}. Nothing was deleted.")

# --- Query item quantity with consensus check ---

def query_item_quantity():
    print("\n--- Query Item Quantity ---")

    item_id = input("Please Enter the Item ID to Query: ").strip()
    results = {}

    # Query each node independently
    for node_name, filename in Inventory_Files.items():
        inventory_data  = load_inventory(filename)
        found_quantity  = None

        for item in inventory_data:
            if str(item["item_id"]).strip() == item_id:
                found_quantity = item["quantity"]
                break

        results[node_name] = found_quantity

    print("\nQuery Results:")
    for node_name, quantity in results.items():
        if quantity is None:
            print(f"{node_name}: Item not found")
        else:
            print(f"{node_name}: Quantity = {quantity}")

    valid_results = [q for q in results.values() if q is not None]

    if len(valid_results) == 0:
        print("\nFinal Result: Item does not exist in the inventory system.")
        return

    # Consensus passes only when all 4 nodes found the item and agree on the quantity
    if len(set(valid_results)) == 1 and len(valid_results) == len(Inventory_Files):
        print("\nConsensus: All inventory nodes agree.")
        print(f"Final Quantity of Item {item_id}: {valid_results[0]}")
    else:
        print("\nConsensus: Inventory nodes do NOT agree.")
        print("Final Result: Query result cannot be trusted.")

# --- RSA signature test (development only) ---

def test_record_signature():
    print("\n--- Testing RSA Signature for an Inventory Record ---")

    test_record = {
        "item_id":  "004",
        "quantity": 12,
        "price":    18,
        "location": "A"
    }

    signer = "A"
    keys   = Inventory_Keys[signer]

    hash_hex, hash_int = hash_record(test_record)
    signature          = rsa_sign(hash_int, keys["d"], keys["n"])
    recovered_hash     = rsa_verify(signature, keys["e"], keys["n"])

    print("\nRecord:",          test_record)
    print("\nHash Hex:",        hash_hex)
    print("\nHash Integer:",    hash_int)
    print("\nSignature:",       signature)
    print("\nRecovered Hash:",  recovered_hash)

    if recovered_hash == hash_int:
        print("\nSignature Verification: VALID")
    else:
        print("\nSignature Verification: INVALID")

# --- Main menu ---

def main_menu():
    while True:
        print("\n==== Secure DLT Inventory System ====")
        print("1. View all Inventory Nodes")
        print("2. Add new Inventory Record")
        print("3. Query Item Quantity")
        print("4. Delete Inventory Record")
        print("5. Exit")
        print("6. TEST RSA SIGNATURE")

        choice = input("Choose an option: ")

        if   choice == "1": view_all_inventories()
        elif choice == "2": add_new_record()
        elif choice == "3": query_item_quantity()
        elif choice == "4": delete_record()
        elif choice == "6": test_record_signature()
        elif choice == "5":
            print("\nExiting system.")
            break
        else:
            print("\nInvalid option. Please choose 1–5.")

main_menu()
