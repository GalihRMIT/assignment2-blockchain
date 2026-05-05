import json
from crypto_utils import generate_rsa_values, hash_record, rsa_sign, rsa_verify

#This is to hold all of the inventory file path in one location. 
Inventory_Files = {
    "Inventory A": "data/inventory_A.json",
    "Inventory B": "data/inventory_B.json",
    "Inventory C": "data/inventory_C.json",
    "Inventory D": "data/inventory_D.json"
}

#list of all of the RSA key values from the given assignment 2 list of key document
Inventory_Keys = {
    "A": generate_rsa_values(
        p=1210613765735147311106936311866593978079938707,
        q=1247842850282035753615951347964437248190231863,
        e=815459040813953176289801

    ),

    "B": generate_rsa_values(
        p=787435686772982288169641922308628444877260947,
        q=1325305233886096053310340418467385397239375379,
        e=692450682143089563609787

    ),

    "C": generate_rsa_values(
        p=1014247300991039444864201518275018240361205111,
        q=904030450302158058469475048755214591704639633,
        e=1158749422015035388438057

    ),

    "D": generate_rsa_values(
        p=1287737200891425621338551020762858710281638317,
        q=1330909125725073469794953234151525201084537607,
        e=33981230465225879849295979

    ),

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

    new_record = {
        "item_id": item_id,
        "quantity": quantity,
        "price": price,
        "location": location
    }

    inventory_check = load_inventory("data/inventory_A.json")

    for item in inventory_check:
        if item ["item_id"] == item_id:
            print("\nOh no Error: The Item ID already exists. Record rejected :( .")
            return

    for filename in Inventory_Files.values():
        inventory_data = load_inventory(filename)
        inventory_data.append(new_record)
        save_inventory(filename, inventory_data)

    print("\nNew Record Created")
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