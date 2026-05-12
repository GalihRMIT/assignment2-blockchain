import json
from backend.key_store import Inventory_Keys
from backend.crypto_utils import generate_rsa_values, hash_record, rsa_sign, rsa_verify

#This is to hold all of the inventory file path in one location. 
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
    with open (filename, "w") as file:
        json.dump(data, file, indent=4)
    
def show_inventory(node_name, data):
    print (f"\n--- {node_name} ---")

    for item in data:
        print(
            f"ID: {item['item_id']} | "
            f"QTY: {item['quantity']} | "
            f"Price: {item['price']} | "
            f"Loc: {item['location']} | "
        )

def view_all_inventories():
    for node_name, filename in Inventory_Files.items():
        inventory_data = load_inventory(filename)
        show_inventory(node_name, inventory_data)

def add_new_record():
    print("\n--- Add a Brand New Inventory Record ---")

    item_id = input("Enter The Item ID: ")
    quantity = int(input("Enter Quantity: "))
    price = int(input("Enter The Price: "))
    location = input("Enter Location (A/B/C/D): ").upper()
    signer = input("Which Invnetory Node is submitting this Record? (A/B/C/D): ").upper().strip()

    if signer not in Inventory_Keys:
        print("\nInvalid Inventory node. Record is Rejected :( .")
        return

    new_record = {
        "item_id": item_id,
        "quantity": quantity,
        "price": price,
        "location": location
    }

    inventory_check = load_inventory("data/inventory_A.json")

    for item in inventory_check:
        if str (item ["item_id"]) == item_id:
            print("\nOh no Error: The Item ID already exists. Record rejected :( .")
            return
        
    signer_keys = Inventory_Keys[signer]

    hash_hex, hash_int = hash_record(new_record)
    signature = rsa_sign(hash_int, signer_keys["d"], signer_keys["n"])

    print("\n--- Digital Signature Process ---")
    print(f"Submitting Node: Inventory {signer}")
    print(f"Record Hash Hex: {hash_hex}")
    print(f"Record Hash Integer: {hash_int}")
    print(f"Digital Signature: {signature}")
    
    #The other Inventory nodes would vewrify utilizing the sender's public key
    print("\n--- Signature Verification is done by other Inventory Nodes ---")

    verification_result = {}

    for node in Inventory_Keys:
        if node != signer:
            recovered_hash = rsa_verify(signature, signer_keys["e"], signer_keys["n"])

            if recovered_hash == hash_int:
                verification_result[node] = "VALID"
                print(f"Inventory {node} Verification: VALID")
            else:
                verification_result[node] = "INVALID"
                print(f"Inventory {node} Verification: INVALID")
        
    if "INVALID" in verification_result.values():
        print("\nFinal Signature Result: INVALID")
        print("The record is Rejected before storage")
        return
        
    print("\nFinal Signature Result: VALID")
    print("All the recieveing nodes are verified by the sender's signature. ")

    for filename in Inventory_Files.values():
        inventory_data = load_inventory(filename)
        inventory_data.append(new_record)
        save_inventory(filename, inventory_data)

    print("\nNew Record Created and Added to all Inventory nodes :) ")
    print(
        f"ID: {new_record['item_id']} | "
        f"QTY: {new_record['quantity']} | "
        f"Price: {new_record['price']} | "
        f"Loc: {new_record['location']} | "
    )

def delete_record():
    print("\n--- Delete Inventory Record ---")

    item_id = input ("Please Enter the Item ID to Delete: ").strip()

    found = False

    for node_name, filename in Inventory_Files.items():
        inventory_data = load_inventory(filename)

        updated_inventory = []
        for item in inventory_data:
            if str(item["item_id"]).strip() != item_id:
                updated_inventory.append(item)
            else:
                found = True
        
        save_inventory(filename, updated_inventory)

    if found:
        print(f"\nRecord with Item ID {item_id} has been deleted from all of the inventory nodes")
    else:
        print(f"\nNo Record found with Item ID of {item_id}. This stayed the same nothing was deleted")

def query_item_quantity():
    print("\n--- This is the Query Item Quantity")

    item_id = input("Please Enter the Item ID to Query: ").strip()

    results = {}

    for node_name, filename in Inventory_Files.items():
        inventory_data = load_inventory(filename)

        found_quantity = None

        for item in inventory_data:
            if str(item["item_id"]).strip() == item_id:
                found_quantity = item["quantity"]
                break
        
        results[node_name] = found_quantity

    print("\nThe Query Results:") 

    for node_name, quantity in results.items():
        if quantity is None:
            print(f"{node_name}: The Item is not Found")
        else:
            print(f"{node_name}: Quantity = {quantity}")
        
    valid_results = [quantity for quantity in results.values() if quantity is not None]

    if len(valid_results) == 0:
        print("\nThe Final Result: Look Item does not exist in the Inventory System.")
        return
        
    if len(set(valid_results)) == 1 and len(valid_results) == len(Inventory_Files):
        print("\nHere is the Consensus Check: All inventory nodes agree")
        print(f"Final Quantity of the Item {item_id}: {valid_results[0]}")
    else:
        print("\nThe Consensus Check: Inventory nodes do NOT Agree.")
        print("Final Result: Query result cannot be trusted")

#TESTING THE RECORD SIGNATURE SYSTEM
def test_record_signature():
    print("\n---Testing the RSA signature for the Inventory Record")

    test_record = {
        "item_id": "004",
        "quantity": 12,
        "price": 18,
        "location": "A"

    }

    signer = "A"
    keys = Inventory_Keys[signer]

    hash_hex, hash_int = hash_record(test_record)
    signature = rsa_sign(hash_int, keys["d"], keys["n"])
    recovered_hash = rsa_verify(signature, keys["e"], keys["n"])

    print("\nRecord:")
    print(test_record)

    print("\nRecord the Hash Hex:")
    print(hash_hex)

    print("\nRecord Hash Integer:")
    print(hash_int)

    print("\nSignature:")
    print(signature)
    
    print("\nRecovered Hash from Signature:")
    print(recovered_hash)

    if recovered_hash == hash_int:
        print("\n Signature Verification VALID")
    else:
        print("\nSignature Verification: INVALID")

#-------------

def main_menu():
    while True:
        print("\n==== Secure DLT Inventory System ====")
        print("1. View all Inventory Nodes")
        print("2. Add new Inventory Record")
        print("3. Query Item Quantity")
        print("4. Delete Inventory record")
        print("5. Exit")
        print("6. TEST RSA SIGNATURE") #TESTING

        choice = input("Choose these option: ")

        if choice == "1":
            view_all_inventories()

        elif choice =="2":
            add_new_record()
        
        elif choice =="3":
            query_item_quantity()

        elif choice =="4":
            delete_record()

        elif choice == "6": # TESTING
            test_record_signature()

        elif choice =="5":
            print("\nExit Da system")
            break
        
        else:
            print("\nInvalid option. Please choose 1, 2, 3, 4 or 5.")

main_menu ()