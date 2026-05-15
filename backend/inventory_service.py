import json
import os
from hashlib import md5
from key_store import Inventory_Keys
from crypto_utils import hash_record, rsa_sign, rsa_verify

# RSA key construction used by PKG:
#   n = p * q (modulus)
#   phi_n = (p-1) * (q-1) (Euler's totient)
#   d= e^(-1) mod phi_n  (private exponent, modular inverse of e)
_KEYS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ListofKeys.json")
with open(_KEYS_PATH) as _f:
    _KEYS = json.load(_f)

# Load the PKG's RSA parameters from the key store
_pkg_p   = _KEYS["PKG"]["p"]
_pkg_q   = _KEYS["PKG"]["q"]
_pkg_e   = _KEYS["PKG"]["e"]
_pkg_n   = _pkg_p * _pkg_q           # n = p * q
_pkg_phi = (_pkg_p - 1) * (_pkg_q - 1)  # phi(n) = (p-1)(q-1)
_pkg_d   = pow(_pkg_e, -1, _pkg_phi) # d = e^-1 mod phi(n)  ← PKG private key

# Load each node's identity, random values, and PKG-issued secret key:
# _node_ids = the value assigned to each node by the PKG
# _node_rand = a per-session random value r_j used as a randomizer
# _node_secrets = g_j = ID_j ^ pkg_d mod pkg_n  (the node's Harn secret key)
_NODE_LBLS    = ["A", "B", "C", "D"]
_node_ids     = [_KEYS["InventoryIDs"][k] for k in _NODE_LBLS]
_node_rand    = [_KEYS["RandomValues"][k]  for k in _NODE_LBLS]
_node_secrets = [pow(iid, _pkg_d, _pkg_n)  for iid in _node_ids]

# RSA key construction (same standard approach as PKG):
#   n = p * q
#   phi_n = (p-1) * (q-1)
#   d = e^(-1) mod phi_n  -PO private key 
#   e, n  -PO public key 

# Load the Procurement Officer's RSA parameters from the key store
_po_p   = _KEYS["ProcurementOfficer"]["p"]
_po_q   = _KEYS["ProcurementOfficer"]["q"]
_po_e   = _KEYS["ProcurementOfficer"]["e"]
_po_n   = _po_p * _po_q           # n = p * q
_po_phi = (_po_p - 1) * (_po_q - 1)  # phi(n) = (p-1)(q-1)
_po_d   = pow(_po_e, -1, _po_phi) # d = e^-1 mod phi(n)  ← PO private key

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

def query_quantity(item_id):
    item_id = str(item_id).strip()

    # LOCATE THE ITEM
    # Loop through every JSON file in each node until we find a matching item_id.
    # Because all nodes have the same records (replicated in add_record), we only need to find it in one file then stop.
    found_item = None
    for filename in Inventory_Files.values():
        for item in load_inventory(filename):
            if str(item["item_id"]).strip() == item_id:
                found_item = item
                break
        if found_item:
            break

    # If the item doesn't exist in any node, return early with failure
    if found_item is None:
        return {
            "success": False,
            "message": f"Item {item_id} not found in any inventory node.",
            "lines": [],
            "consensus_result": "NO RESULT"
        }

    # Pull the quantity out from record, this is what the PO or the message is querying
    qty = found_item["quantity"]

    # Initialise cryptographic parameters
    # Build the lines[] list that will be displayed in the UI step-by-step.
    # PKG RSA key construction (standard RSA):
    #   n = p * q
    #   phi_n = (p-1) * (q-1) Euler's totient
    #   d = e^(-1) mod phi_n private key (modular inverse of e)
    #
    # The PKG's role here: it computed each node's secret key g_j offline as:
    #   g_j = ID_j ^ d mod n
    # This means g_j is the PKG's RSA signature over that node's identity.
    # Nodes use g_j later when computing their partial Harn signature.
    lines = [
        "1. CRYPTOGRAPHIC PARAMETER INITIALISATION",
        "",
        "[PKG - Private Key Generator]",
        f"  p     = {_pkg_p}",
        f"  q     = {_pkg_q}",
        f"  e     = {_pkg_e}",
        f"  n     = {_pkg_n}",
        f"  phi_n = {_pkg_phi}",
        f"  d     = {_pkg_d}",
        "[Procurement Officer - RSA Key Pair]",
        f"  p     = {_po_p}",
        f"  q     = {_po_q}",
        f"  e     = {_po_e}",
        f"  n     = {_po_n}",
        f"  phi_n = {_po_phi}",
        f"  d     = {_po_d}",
        "",
        "[Inventory Nodes: Identities, Random Values, Secret Keys]",
        # Each node j has:
        #   ID_j  = its unique numeric identity
        #   r_j   = a per-session random value (nonce)
        #   g_j   = ID_j ^ pkg_d mod pkg_n  (secret key issued by PKG)
    ]
    for lbl, iid, r, g in zip(_NODE_LBLS, _node_ids, _node_rand, _node_secrets):
        lines.append(f"  Node {lbl}:  ID = {iid},  r = {r}")
        lines.append(f"           g_{lbl} = {g}")
    lines += [
        "",
        "-----------------------------------------------------------------",
        f"  Query received: Item {item_id}",
        "  Forwarding to all inventory nodes for collective approval",
        "-----------------------------------------------------------------",
    ]

    # Harn Multi-Signature
    # The Harn scheme lets ALL four nodes jointly sign a message so that the combined signature can be verified against ALL identities at once.
    # No single node's partial signature is valid on its own, they must all cooperate, which prevents any one node from faking the response.
    # The message being signed is the query result itself:
    m = f"Item {item_id}: quantity = {qty}"

    # 2a. Partial Commitments: t_j = r_j ^ e mod n
    # Each node j raises its random value r_j to the PKG public exponent e.
    # Formula:  t_j = r_j ^ pkg_e  mod  pkg_n
    t_vals = [pow(r, _pkg_e, _pkg_n) for r in _node_rand]

    # The combined commitment t is the product of all t_j values mod n.
    # Formula:  t = t_A * t_B * t_C * t_D  mod  pkg_n
    t = 1
    for tv in t_vals:
        t = t * tv % _pkg_n

    # 2b. Hash: h = MD5( str(t) || m )
    # Concatenate the combined commitment t (as a string) with the message m, then hash with MD5. This binds the signature to both the nonces and
    # the message content, changing either would produce a different h.
    # Formula:  h = MD5( str(t) + m )  =  convert hex digest to integer
    h_hex = md5((str(t) + m).encode()).hexdigest()
    h_int = int(h_hex, 16)   # convert hex string = big integer for arithmetic

    # 2c. Partial Signatures: s_j = g_j * r_j ^ h  mod n
    # Each node j combines its PKG-issued secret g_j with its random value raised to the hash power h. This ties the node's identity and its
    # commitment together under the challenge h.
    # Formula:  s_j = g_j * (r_j ^ h_int)  mod  pkg_n
    s_vals = [g * pow(r, h_int, _pkg_n) % _pkg_n
              for g, r in zip(_node_secrets, _node_rand)]

    # 2d. Combined Signature: s = s_A * s_B * s_C * s_D  mod n
    # Multiply all partial signatures together to get the single group signature s that represents all four nodes' agreement.
    # Formula:  s = s_A * s_B * s_C * s_D  mod  pkg_n
    s = 1
    for sv in s_vals:
        s = s * sv % _pkg_n

    # 2e. Signature Verification
    # To verify s without knowing any private keys, a verifier checks:
    # LHS = s ^ pkg_e  mod  pkg_n
    # RHS = (i_A * i_B * i_C * i_D) * t ^ h_int  mod  pkg_n
    # Why this works (the math):
    # s = prod(g_j * r_j^h) = prod(ID_j^d * r_j^h)
    # s^e = prod(ID_j^(d*e)) * prod(r_j^(h*e))
    #     = prod(ID_j)        * prod(t_j)^h          [since d*e ≡ 1 mod phi_n]
    #     = prod(ID_j)        * t^h
    # So LHS == RHS proves every node participated correctly.
    lhs = pow(s, _pkg_e, _pkg_n)

    # Product of all node identity values mod n
    prod_ids = 1
    for iid in _node_ids:
        prod_ids = prod_ids * iid % _pkg_n

    # RHS = prod(ID_j) * t ^ h  mod  n
    rhs = prod_ids * pow(t, h_int, _pkg_n) % _pkg_n

    # verified = True means the group signature is mathematically valid
    verified = (lhs == rhs)

    lines += [
        "",
        "2.  HARN MULTI-SIGNATURE",
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
        f"  Result: {'VERIFIED, signature is valid' if verified else 'FAILED, signature invalid'}",
        "-----------------------------------------------------------------",
    ]

    # STEP 3: RSA Encryption (protect approved response)
    # Now that the nodes have collectively signed the result, we encrypt the message with the Procurement Officer's PUBLIC key (po_e, po_n).
    # RSA encryption: ciphertext = msg_int ^ po_e  mod  po_n
    
    # Only the PO who holds the matching private key po_d can decrypt.
    # This ensures that even if the signed result is intercepted in transit, nobody but the PO can read the actual quantity.
    
    # Step 1: encode the text message to bytes, then interpret those bytes as one big integer so we can apply modular exponentiation.
    msg_bytes  = m.encode()
    msg_int    = int.from_bytes(msg_bytes, 'big')  # bytes = integer (big-endian)

    # Step 2: RSA encrypt using PO's public key
    # Formula: ciphertext = msg_int ^ po_e  mod  po_n
    ciphertext = pow(msg_int, _po_e, _po_n)

    lines += [
        "",
        " 3. SECURE DELIVERY: ENCRYPT APPROVED RESPONSE",
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

    # STEP 4: PO Decrypts and Verifies 
    # The Procurement Officer uses their PRIVATE key (po_d) to decrypt.
    # RSA decryption: recovered_int = ciphertext ^ po_d  mod  po_n
    
    # Because RSA is a trapdoor function, only someone with po_d can reverse the encryption done with po_e
    # So recovered_int == msg_int if everything went correctly.
    recovered_int = pow(ciphertext, _po_d, _po_n)

    # Convert the integer back into bytes, then decode to a string.
    # bit_length()+7)//8 gives the minimum number of bytes needed.
    recovered_bytes = recovered_int.to_bytes((recovered_int.bit_length() + 7) // 8, 'big')
    recovered_msg   = recovered_bytes.decode()

    # content_ok = True if the decrypted text exactly matches the original
    # message m.  Any tampering with the ciphertext would corrupt this.
    content_ok = (recovered_msg == m)

    # Re-run the Harn verification on the RECOVERED message (not the original).
    # This is the PO's independent check, they recompute h using the decrypted message and then confirm that s^e mod n still equals prod(IDs)*t^h mod n.
    # If the ciphertext was altered in transit, recovered_msg != m = h_rec != h_int = the LHS/RHS won't match = sig_ok = False.
    
    # Formula (same as Step 2e, but using the PO's recovered message):
    # h_rec = MD5( str(t) + recovered_msg ) as integer
    # lhs_rec = s ^ pkg_e  mod  pkg_n
    # rhs_rec = prod(IDs)  * t ^ h_rec  mod  pkg_n
    h_rec   = int(md5((str(t) + recovered_msg).encode()).hexdigest(), 16)
    lhs_rec = pow(s, _pkg_e, _pkg_n)
    rhs_rec = prod_ids * pow(t, h_rec, _pkg_n) % _pkg_n

    # sig_ok = True means the Harn signature holds on the decrypted message
    sig_ok = (lhs_rec == rhs_rec)

    # FINAL RESULT
    # The query is APPROVED only when BOTH conditions hold:
    # sig_ok = the group signature is valid (all nodes agreed, message was not tampered with after signing)
    # content_ok = the decrypted message is exactly what was signed (encryption/decryption round-trip was clean)
    # If either fails the response is REJECTED, the PO cannot trust the data.

    lines += [
        "",
        " 4. PROCUREMENT OFFICER: DECRYPT AND VERIFY",
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
        f"  Result: {'APPROVED, response is authentic and unaltered' if (sig_ok and content_ok) else 'REJECTED, verification failed'}",
        "-----------------------------------------------------------------",
    ]

    return {
        "success": sig_ok and content_ok,
        "message": f"Item {item_id} queried, {'APPROVED' if (sig_ok and content_ok) else 'REJECTED'}.",
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