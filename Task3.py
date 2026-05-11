from flask import Flask, jsonify, request
from hashlib import md5
import json, os

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────────
#  Load keys
# ─────────────────────────────────────────────────────────────────
KEYS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ListofKeys.json")
with open(KEYS_PATH) as f:
    KEYS = json.load(f)

# ─────────────────────────────────────────────────────────────────
#  STEP 1 — Compute all cryptographic parameters at startup
# ─────────────────────────────────────────────────────────────────

# PKG
pkg_p   = KEYS["PKG"]["p"]
pkg_q   = KEYS["PKG"]["q"]
pkg_e   = KEYS["PKG"]["e"]
pkg_n   = pkg_p * pkg_q
pkg_phi = (pkg_p - 1) * (pkg_q - 1)
pkg_d   = pow(pkg_e, -1, pkg_phi)          # master secret

# Procurement Officer (querying user)
po_p   = KEYS["ProcurementOfficer"]["p"]
po_q   = KEYS["ProcurementOfficer"]["q"]
po_e   = KEYS["ProcurementOfficer"]["e"]
po_n   = po_p * po_q
po_phi = (po_p - 1) * (po_q - 1)
po_d   = pow(po_e, -1, po_phi)             # PO private decryption key

# Inventory nodes — identities, random values, PKG-issued secret keys
NODE_LBLS    = ["A", "B", "C", "D"]
node_ids     = [KEYS["InventoryIDs"][k]  for k in NODE_LBLS]   # [126,127,128,129]
node_rand    = [KEYS["RandomValues"][k]  for k in NODE_LBLS]   # [621,721,821,921]
node_secrets = [pow(iid, pkg_d, pkg_n)   for iid in node_ids]  # gj = ij^d mod n

# Inventory records keyed by inventory ID
INVENTORY = {"126": 32, "127": 20, "128": 22, "129": 12}

# ─────────────────────────────────────────────────────────────────
#  API — query: Step 1 params + Step 3 Harn multi-signature
# ─────────────────────────────────────────────────────────────────

@app.route("/api/query", methods=["POST"])
def query():
    data    = request.get_json()
    item_id = data.get("item_id", "")
    qty     = INVENTORY.get(item_id)

    if qty is None:
        return jsonify({"error": "Item not found"}), 404

    # ── STEP 1 output ──────────────────────────────────────────────
    lines = [
        "=================================================================",
        "  STEP 1: CRYPTOGRAPHIC PARAMETER INITIALISATION",
        "=================================================================",
        "",
        "[PKG - Private Key Generator]",
        f"  p     = {pkg_p}",
        f"  q     = {pkg_q}",
        f"  e     = {pkg_e}",
        f"  n     = {pkg_n}",
        f"  phi_n = {pkg_phi}",
        f"  d     = {pkg_d}",
        f"          (master secret - kept private)",
        "",
        "[Procurement Officer - RSA Key Pair]",
        f"  p     = {po_p}",
        f"  q     = {po_q}",
        f"  e     = {po_e}   (public - encrypts response)",
        f"  n     = {po_n}",
        f"  phi_n = {po_phi}",
        f"  d     = {po_d}",
        f"          (private - decrypts response)",
        "",
        "[Inventory Nodes - Identities, Random Values, Secret Keys]",
    ]
    for lbl, iid, r, g in zip(NODE_LBLS, node_ids, node_rand, node_secrets):
        lines.append(f"  Node {lbl}:  ID = {iid},  r = {r}")
        lines.append(f"           g_{lbl} = {g}")
    lines += [
        "",
        "  Step 1 complete - all parameters initialised.",
        "-----------------------------------------------------------------",
        "",
        f"  Query received: Inventory {item_id}",
        "  Forwarding to all inventory nodes for collective approval...",
        "-----------------------------------------------------------------",
    ]

    # ── STEP 3: Harn Multi-Signature ───────────────────────────────

    # Message being signed = the approved query result
    m = f"Inventory {item_id}: quantity = {qty}"

    # 3a. Partial commitments:  tj = rj^e mod n
    t_vals = [pow(r, pkg_e, pkg_n) for r in node_rand]
    t      = 1
    for tv in t_vals:
        t = t * tv % pkg_n

    # 3b. Hash:  h = MD5(str(t) || m)
    c_m   = str(t) + m
    h_hex = md5(c_m.encode()).hexdigest()
    h_int = int(h_hex, 16)

    # 3c. Partial signatures:  sj = gj * rj^h mod n
    s_vals = []
    for g, r in zip(node_secrets, node_rand):
        sj = g * pow(r, h_int, pkg_n) % pkg_n
        s_vals.append(sj)

    # 3d. Combined signature
    s = 1
    for sv in s_vals:
        s = s * sv % pkg_n

    # 3e. Verify:  s^e mod n == (prod ij) * t^h mod n
    lhs      = pow(s, pkg_e, pkg_n)
    prod_ids = 1
    for iid in node_ids:
        prod_ids = prod_ids * iid % pkg_n
    rhs      = prod_ids * pow(t, h_int, pkg_n) % pkg_n
    verified = (lhs == rhs)

    # ── STEP 3 output ──────────────────────────────────────────────
    lines += [
        "",
        "=================================================================",
        "  STEP 3: HARN MULTI-SIGNATURE",
        "=================================================================",
        "",
        f"  Message (m) : \"{m}\"",
        "",
        "[3a. Partial Commitments:  tj = rj^e mod n]",
    ]
    for lbl, r, tv in zip(NODE_LBLS, node_rand, t_vals):
        lines.append(f"  t_{lbl} = {r}^e mod n")
        lines.append(f"      = {tv}")
    lines += [
        "",
        f"  t = t_A * t_B * t_C * t_D mod n",
        f"    = {t}",
        "",
        "[3b. Hash:  h = MD5(str(t) || m)]",
        f"  c_m   = str(t) + m",
        f"  h_hex = MD5(c_m) = {h_hex}",
        f"  h     = int(h_hex, 16)",
        f"        = {h_int}",
        "",
        "[3c. Partial Signatures:  sj = gj * rj^h mod n]",
    ]
    for lbl, g, r, sv in zip(NODE_LBLS, node_secrets, node_rand, s_vals):
        lines.append(f"  s_{lbl} = g_{lbl} * {r}^h mod n")
        lines.append(f"      = {sv}")
    lines += [
        "",
        f"  s = s_A * s_B * s_C * s_D mod n",
        f"    = {s}",
        "",
        "[3d. Verification:  s^e mod n == (i_A * i_B * i_C * i_D) * t^h mod n]",
        f"  LHS = s^e mod n",
        f"      = {lhs}",
        f"  RHS = (i_A * i_B * i_C * i_D) * t^h mod n",
        f"      = {rhs}",
        "",
        f"  Result: {'VERIFIED - signature is valid' if verified else 'FAILED - signature invalid'}",
        "-----------------------------------------------------------------",
    ]

    # ── STEP 4: RSA Encryption — protect approved response ────────────

    msg_bytes  = m.encode()
    msg_int    = int.from_bytes(msg_bytes, 'big')
    ciphertext = pow(msg_int, po_e, po_n)          # c = m^e mod n (PO public key)

    lines += [
        "",
        "=================================================================",
        "  STEP 4: SECURE DELIVERY — ENCRYPT APPROVED RESPONSE",
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

    # ── STEP 5: PO Decrypts and Verifies ──────────────────────────────

    # Decrypt:  m = c^d mod n
    recovered_int   = pow(ciphertext, po_d, po_n)
    recovered_bytes = recovered_int.to_bytes((recovered_int.bit_length() + 7) // 8, 'big')
    recovered_msg   = recovered_bytes.decode()

    # Re-run Harn verification on the recovered message
    c_m_rec     = str(t) + recovered_msg
    h_rec       = int(md5(c_m_rec.encode()).hexdigest(), 16)
    lhs_rec     = pow(s, pkg_e, pkg_n)
    rhs_rec     = prod_ids * pow(t, h_rec, pkg_n) % pkg_n
    sig_ok      = (lhs_rec == rhs_rec)
    content_ok  = (recovered_msg == m)

    lines += [
        "",
        "=================================================================",
        "  STEP 5: PROCUREMENT OFFICER — DECRYPT AND VERIFY",
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
        f"  Result: {'APPROVED  — response is authentic and unaltered' if (sig_ok and content_ok) else 'REJECTED  — verification failed'}",
        "-----------------------------------------------------------------",
    ]

    return jsonify({"lines": lines, "item_id": item_id, "qty": qty,
                    "verified": verified, "sig_ok": sig_ok, "content_ok": content_ok})

# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Backend running on http://localhost:5000")
    app.run(debug=True, port=5000)
