import json

def load_inventory(filename):
    with open(filename, "r") as file:
        return json.load(file)
    
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
    inventory_A = load_inventory("data/inventory_A.json")
    inventory_B = load_inventory("data/inventory_B.json")
    inventory_C = load_inventory("data/inventory_C.json")
    inventory_D = load_inventory("data/inventory_D.json")
    
    show_inventory("Inventory A", inventory_A)
    show_inventory("Inventory B", inventory_B)
    show_inventory("Inventory C", inventory_C)
    show_inventory("Inventory D", inventory_D)

def save_inventory(filename, data):
    with open (filename, "w") as file:
        json.dump(data, file, indent=4)

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

    #This will be to load all of the invnetories
    inventory_A = load_inventory("data/inventory_A.json")
    inventory_B = load_inventory("data/inventory_B.json")
    inventory_C = load_inventory("data/inventory_C.json")
    inventory_D = load_inventory("data/inventory_D.json")

    inventory_A.append(new_record)
    inventory_B.append(new_record)
    inventory_C.append(new_record)
    inventory_D.append(new_record)

    save_inventory("data/inventory_A.json", inventory_A)
    save_inventory("data/inventory_B.json", inventory_B)
    save_inventory("data/inventory_C.json", inventory_C)
    save_inventory("data/inventory_D.json", inventory_D)

    print("\nNew Record Created")
    print(
        f"ID: {new_record['item_id']} | "
        f"QTY: {new_record['quantity']} | "
        f"Price: {new_record['price']} | "
        f"Loc: {new_record['location']} | "
    )

def main_menu():
    while True:
        print("\n==== Secure DLT Inventory System ====")
        print("1. View all Inventory Nodes")
        print("2. Add new Inventory Record")
        print("3. Query Item Quantity")
        print("4. Exit")

        choice = input("Choose these option: ")

        if choice == "1":
            view_all_inventories()

        elif choice =="2":
            add_new_record()
        
        elif choice =="3":
            print("\nMore Feature incoming")

        elif choice =="4":
            print("\nExit Da system")
            break
        
        else:
            print("\nInvalid option. Please choose 1, 2, 3, or 4.")

main_menu ()