// crypto.js
// JavaScript port of crypto_utils.py — all RSA and hashing logic runs here
// in the browser using native BigInt (for large-number arithmetic) and the
// Web Crypto API (for SHA-256). No backend or external libraries needed.

// ─── Modular exponentiation ────────────────────────────────────────────────
// Computes base^exp mod mod efficiently using repeated squaring.
// Equivalent to Python's built-in pow(base, exp, mod).
function modPow(base, exp, mod) {
  let result = 1n
  base = base % mod
  while (exp > 0n) {
    if (exp & 1n) result = result * base % mod // multiply when current bit is 1
    exp >>= 1n                                  // shift to next bit
    base = base * base % mod                    // square the base
  }
  return result
}

// ─── Modular inverse via extended Euclidean algorithm ─────────────────────
// Finds x such that (a * x) ≡ 1 (mod m).
// Used to compute d = e⁻¹ mod φ(n) — the RSA private key.
function modInverse(a, m) {
  let [r0, r1] = [a, m]
  let [s0, s1] = [1n, 0n]
  while (r1 !== 0n) {
    const q = r0 / r1
    ;[r0, r1] = [r1, r0 - q * r1]
    ;[s0, s1] = [s1, s0 - q * s1]
  }
  return ((s0 % m) + m) % m // ensure positive result
}

// ─── RSA key generation ────────────────────────────────────────────────────
// Derives all 6 RSA values from the assignment-provided p, q, and e.
// Mirrors generate_rsa_values() in crypto_utils.py exactly.
function makeKey(p, q, e) {
  const n   = p * q              // public modulus
  const phi = (p - 1n) * (q - 1n) // Euler's totient
  const d   = modInverse(e, phi) // private key: e⁻¹ mod φ(n)
  return { p, q, e, n, phi, d }
}

// ─── Node key pairs (fixed by the assignment) ─────────────────────────────
// Computed once at module load. Each entry exposes p, q, n, phi, e (public), d (private).
export const KEYS = {
  A: makeKey(
    1210613765735147311106936311866593978079938707n,
    1247842850282035753615951347964437248190231863n,
    815459040813953176289801n
  ),
  B: makeKey(
    787435686772982288169641922308628444877260947n,
    1325305233886096053310340418467385397239375379n,
    692450682143089563609787n
  ),
  C: makeKey(
    1014247300991039444864201518275018240361205111n,
    904030450302158058469475048755214591704639633n,
    1158749422015035388438057n
  ),
  D: makeKey(
    1287737200891425621338551020762858710281638317n,
    1330909125725073469794953234151525201084537607n,
    33981230465225879849295979n
  ),
}

// ─── SHA-256 hashing ───────────────────────────────────────────────────────
// Mirrors hash_record() + record_to_string() in crypto_utils.py.
// Returns { str, hex, int } — the canonical string, its hex digest, and
// the digest as a BigInt ready for RSA modular exponentiation.
export async function hashRecord(record) {
  // Serialize to the same fixed format Python uses: "item_id,quantity,price,location"
  const str = `${record.item_id},${record.quantity},${record.price},${record.location}`

  // SHA-256 via the browser's built-in Web Crypto API (identical output to Python's hashlib)
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str))
  const hex = Array.from(new Uint8Array(buf))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')

  const int = BigInt('0x' + hex) // convert hex digest to integer for RSA input

  return { str, hex, int }
}

// ─── RSA sign ──────────────────────────────────────────────────────────────
// signature = hash_int ^ d  mod  n
// Only the node that holds the private key d can produce this value.
export function rsaSign(hashInt, key) {
  return modPow(hashInt, key.d, key.n)
}

// ─── RSA verify ────────────────────────────────────────────────────────────
// recovered = signature ^ e  mod  n
// Any node can verify using only the signer's public key (e, n).
// If recovered === hash_int, the signature is valid.
export function rsaVerify(signature, key) {
  return modPow(signature, key.e, key.n)
}
