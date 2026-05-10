# crypto_utils.py
# Core cryptographic functions for the DLT inventory system.
# Implements RSA key generation, SHA-256 hashing, signing, and verification
# using only Python's standard library (hashlib, math).

import hashlib
from math import gcd

# Finds the modular inverse of e mod phi using Python's built-in pow with exponent -1
def mod_inverse(e, phi):
    return pow(e, -1, phi)

# Derives all RSA key values from the given p, q, and e (provided by the assignment).
# Does NOT generate random keys — it only computes n, phi, and d from the inputs.
def generate_rsa_values(p, q, e):
    n   = p * q              # Public modulus: product of both primes
    phi = (p - 1) * (q - 1) # Euler's totient: number of integers coprime to n

    # e must be coprime with phi for a valid RSA key
    if gcd(e, phi) != 1:
        raise ValueError("Invalid RSA Values: The e and phi are not coprime.")

    d = mod_inverse(e, phi)  # Private key: modular inverse of e mod phi

    return {
        "p":   p,
        "q":   q,
        "e":   e,   # Public exponent — shared openly
        "n":   n,   # Public modulus  — shared openly
        "phi": phi, # Euler's totient — kept secret
        "d":   d    # Private key     — never shared
    }

# Converts a record dict into a fixed comma-separated string for consistent hashing
def record_to_string(record):
    return f"{record['item_id']},{record['quantity']},{record['price']},{record['location']}"

# Hashes a record using SHA-256 and returns both the hex digest and its integer form.
# The integer is needed for RSA modular exponentiation.
def hash_record(record):
    record_string = record_to_string(record)

    hash_hex = hashlib.sha256(record_string.encode()).hexdigest() # 64-char hex string
    hash_int = int(hash_hex, 16)                                  # Convert hex → integer

    return hash_hex, hash_int

# RSA signing: computes signature = hash_int ^ d  mod  n
# Only the node that holds the private key d can produce this value
def rsa_sign(hash_int, d, n):
    signature = pow(hash_int, d, n)
    return signature

# RSA verification: recovers hash = signature ^ e  mod  n
# Any node can do this using only the signer's public key (e, n)
def rsa_verify(signature, e, n):
    recovered_hash = pow(signature, e, n)
    return recovered_hash
