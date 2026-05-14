import json
import os
from hashlib import md5
from key_store import Inventory_Keys
from crypto_utils import hash_record, rsa_sign, rsa_verify

# Load PKG keys for Harn multi-signature
_KEYS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ListofKeys.json")
with open(_KEYS_PATH) as _f:
    _KEYS = json.load(_f)

_pkg_p   = _KEYS["PKG"]["p"]
_pkg_q   = _KEYS["PKG"]["q"]
_pkg_e   = _KEYS["PKG"]["e"]
_pkg_n   = _pkg_p * _pkg_q
_pkg_phi = (_pkg_p - 1) * (_pkg_q - 1)
_pkg_d   = pow(_pkg_e, -1, _pkg_phi)

_NODE_LBLS    = ["A", "B", "C", "D"]
_node_ids     = [_KEYS["InventoryIDs"][k] for k in _NODE_LBLS]
_node_rand    = [_KEYS["RandomValues"][k]  for k in _NODE_LBLS]
_node_secrets = [pow(iid, _pkg_d, _pkg_n)  for iid in _node_ids]

# Procurement Officer keys
_po_p   = _KEYS["ProcurementOfficer"]["p"]
_po_q   = _KEYS["ProcurementOfficer"]["q"]
_po_e   = _KEYS["ProcurementOfficer"]["e"]
_po_n   = _po_p * _po_q
_po_phi = (_po_p - 1) * (_po_q - 1)
_po_d   = pow(_po_e, -1, _po_phi)

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

    # Just loads inventroy A and checks if an existing ID exist 
    inventory_check = load_inventory("data/inventory_A.json")

    # If it does exist it prevents a duplicate ID
    for item in inventory_check:
        if str(item["item_id"]) == str(item_id):
            return {
                "success": False,
                "message": "Item ID already exists. Record rejected."
            }

    # If the singer of the message is A then it takes the key for Inventory A 
    signer_keys = Inventory_Keys[signer]

    # This just transforms the inventory record into a hash 
    hash_hex, hash_int = hash_record(new_record)
    # This creates the RSA digital signiture and proves that the record was signed by the inventroy node that owns the private key d
    signature = rsa_sign(hash_int, signer_keys["d"], signer_keys["n"])

    # This is where the system simulates the other inventory nodes checking for signiture
    # IMPORTANT NOTE: the loop will go rhough every node excpet for the signer node 
    verification_results = {}

    for node in Inventory_Keys:
        if node != signer:
            # add notice to this part where it uses the singers public key and not the verifiers own key 
            recovered_hash = rsa_verify(signature, signer_keys["e"], signer_keys["n"])

            if recovered_hash == hash_int:
                verification_results[f"Inventory {node}"] = "VALID"
            else:
                verification_results[f"Inventory {node}"] = "INVALID"

    # This just rejects any record if even one node says invalid 
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
        "verification_results": verification_results,
        "consensus_result": "ACCEPTED"
    }

def query_quantity(item_id):
    item_id = str(item_id).strip()

    # Search all nodes for the specific item
    found_item = None
    for filename in Inventory_Files.values():
        for item in load_inventory(filename):
            if str(item["item_id"]).strip() == item_id:
                found_item = item
                break
        if found_item:
            break

    if found_item is None:
        return {
            "success": False,
            "message": f"Item {item_id} not found in any inventory node.",
            "lines": [],
            "consensus_result": "NO RESULT"
        }

    qty = found_item["quantity"]

    # ── STEP 1: Initialise cryptographic parameters ───────────────────
    lines = [
        "=================================================================",
        "  STEP 1 — CRYPTOGRAPHIC PARAMETER INITIALISATION",
        "=================================================================",
        "",
        "[PKG - Private Key Generator]",
        f"  p     = {_pkg_p}",
        f"  q     = {_pkg_q}",
        f"  e     = {_pkg_e}",
        f"  n     = {_pkg_n}",
        f"  phi_n = {_pkg_phi}",
        f"  d     = {_pkg_d}",
        f"          (master secret — kept private)",
        "",
        "[Procurement Officer - RSA Key Pair]",
        f"  p     = {_po_p}",
        f"  q     = {_po_q}",
        f"  e     = {_po_e}   (public — encrypts response)",
        f"  n     = {_po_n}",
        f"  phi_n = {_po_phi}",
        f"  d     = {_po_d}",
        f"          (private — decrypts response)",
        "",
        "[Inventory Nodes — Identities, Random Values, Secret Keys]",
    ]
    for lbl, iid, r, g in zip(_NODE_LBLS, _node_ids, _node_rand, _node_secrets):
        lines.append(f"  Node {lbl}:  ID = {iid},  r = {r}")
        lines.append(f"           g_{lbl} = {g}")
    lines += [
        "",
        "-----------------------------------------------------------------",
        f"  Query received: Item {item_id}",
        "  Forwarding to all inventory nodes for collective approval...",
        "-----------------------------------------------------------------",
    ]

    # ── STEP 2: Harn Multi-Signature ─────────────────────────────────
    m = f"Item {item_id}: quantity = {qty}"

    # 2a. Partial commitments: tj = rj^e mod n
    t_vals = [pow(r, _pkg_e, _pkg_n) for r in _node_rand]
    t = 1
    for tv in t_vals:
        t = t * tv % _pkg_n

    # 2b. Hash: h = MD5(str(t) || m)
    h_hex = md5((str(t) + m).encode()).hexdigest()
    h_int = int(h_hex, 16)

    # 2c. Partial signatures: sj = gj * rj^h mod n
    s_vals = [g * pow(r, h_int, _pkg_n) % _pkg_n
              for g, r in zip(_node_secrets, _node_rand)]

    # 2d. Combined signature
    s = 1
    for sv in s_vals:
        s = s * sv % _pkg_n

    # 2e. Verify: s^e mod n == (prod ij) * t^h mod n
    lhs = pow(s, _pkg_e, _pkg_n)
    prod_ids = 1
    for iid in _node_ids:
        prod_ids = prod_ids * iid % _pkg_n
    rhs = prod_ids * pow(t, h_int, _pkg_n) % _pkg_n
    verified = (lhs == rhs)

    lines += [
        "",
        "=================================================================",
        "  STEP 2 — HARN MULTI-SIGNATURE",
        "=================================================================",
        "",
        f"  Message (m) : \"{m}\"",
        "",
        "[2a. Partial Commitments:  tj = rj^e mod n]",
    ]
    for lbl, r, tv in zip(_NODE_LBLS, _node_rand, t_vals):
        lines.append(f"  t_{lbl} = {r}^e mod n = {tv}")
    lines += [
        "",
        f"  t = t_A * t_B * t_C * t_D mod n",
        f"    = {t}",
        "",
        "[2b. Hash:  h = MD5(str(t) || m)]",
        f"  h_hex = {h_hex}",
        f"  h     = {h_int}",
        "",
        "[2c. Partial Signatures:  sj = gj * rj^h mod n]",
    ]
    for lbl, sv in zip(_NODE_LBLS, s_vals):
        lines.append(f"  s_{lbl} = {sv}")
    lines += [
        "",
        f"  s = s_A * s_B * s_C * s_D mod n",
        f"    = {s}",
        "",
        "[2d. Verification:  s^e mod n == (i_A * i_B * i_C * i_D) * t^h mod n]",
        f"  LHS = s^e mod n = {lhs}",
        f"  RHS             = {rhs}",
        "",
        f"  Result: {'VERIFIED — signature is valid' if verified else 'FAILED — signature invalid'}",
        "-----------------------------------------------------------------",
    ]

    # ── STEP 3: RSA Encryption — protect approved response ────────────
    msg_bytes  = m.encode()
    msg_int    = int.from_bytes(msg_bytes, 'big')
    ciphertext = pow(msg_int, _po_e, _po_n)

    lines += [
        "",
        "=================================================================",
        "  STEP 3 — SECURE DELIVERY: ENCRYPT APPROVED RESPONSE",
        "=================================================================",
        "",
        "  Encrypting signed result with Procurement Officer public key",
        "  (po_e, po_n) so only the PO can read it.",
        "",
        f"  Message (m)        : \"{m}\"",
        f"  Message as integer : {msg_int}",
        "",
        "  ciphertext = msg_int ^ po_e mod po_n",
        f"             = {ciphertext}",
        "",
        "  Encrypted response transmitted to Procurement Officer.",
        "-----------------------------------------------------------------",
    ]

    # ── STEP 4: PO Decrypts and Verifies ─────────────────────────────
    recovered_int   = pow(ciphertext, _po_d, _po_n)
    recovered_bytes = recovered_int.to_bytes((recovered_int.bit_length() + 7) // 8, 'big')
    recovered_msg   = recovered_bytes.decode()

    h_rec   = int(md5((str(t) + recovered_msg).encode()).hexdigest(), 16)
    lhs_rec = pow(s, _pkg_e, _pkg_n)
    rhs_rec = prod_ids * pow(t, h_rec, _pkg_n) % _pkg_n
    sig_ok      = (lhs_rec == rhs_rec)
    content_ok  = (recovered_msg == m)

    lines += [
        "",
        "=================================================================",
        "  STEP 4 — PROCUREMENT OFFICER: DECRYPT AND VERIFY",
        "=================================================================",
        "",
        "  Decrypting with Procurement Officer private key (po_d)",
        "",
        "  recovered_int = ciphertext ^ po_d mod po_n",
        f"               = {recovered_int}",
        "",
        f"  Recovered message  : \"{recovered_msg}\"",
        f"  Content match      : {'YES' if content_ok else 'NO'}",
        "",
        "[Re-run Harn Signature Verification on Recovered Message]",
        f"  h (recomputed)     = {h_rec}",
        f"  LHS = s^e mod n    = {lhs_rec}",
        f"  RHS                = {rhs_rec}",
        "",
        f"  Signature valid    : {'YES' if sig_ok else 'NO'}",
        "",
        f"  Result: {'APPROVED — response is authentic and unaltered' if (sig_ok and content_ok) else 'REJECTED — verification failed'}",
        "-----------------------------------------------------------------",
    ]

    return {
        "success": sig_ok and content_ok,
        "message": f"Item {item_id} queried — {'APPROVED' if (sig_ok and content_ok) else 'REJECTED'}.",
        "item": found_item,
        "lines": lines,
        "verified": verified,
        "sig_ok": sig_ok,
        "content_ok": content_ok,
        "consensus_result": "APPROVED" if (sig_ok and content_ok) else "REJECTED"
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