import hashlib
from math import gcd

# Calculates the modular inverse of e modulo phi. 
# Returns d for the RSA private key componenet.
def mod_inverse(e, phi):
    return pow(e, -1, phi)

# NOT CREATING RAMDOM KEYS.
# Taking the given p, q, and e values to calcualtes the n, phi, and d
def generate_rsa_values(p, q, e):
    n = p * q #RSA key generation Formula
    phi = (p - 1) * (q - 1) # Euler's toient calculation

    # Check whether the GCD is 1 and if its not then e cannot be used to calculate the d
    if gcd(e, phi) != 1:
        raise ValueError("Invalid RSA Values: The e and phi are not coprime.")
    
    d = mod_inverse(e, phi) #RSA private component

    return {
        "p":p,  
        "q":q,
        "e":e,
        "n":n,
        "phi":phi,
        "d":d
    }

# This function turns the inventory record from a dictionary to a clear string format
def record_to_string(record):
    return f"{record['item_id']},{record['quantity']},{record['price']},{record['location']}"

# This function took the record from the previous function then uses SHA-256 to create a hash/fingerprint
def hash_record(record):
    record_string = record_to_string(record)

    hash_hex = hashlib.sha256(record_string.encode()).hexdigest()
    # This additionally takes the same hash and converts it into a integer for RSA calculation
    hash_int = int(hash_hex, 16)

    return hash_hex, hash_int

# This function creates the digital signiture
def rsa_sign(hash_int, d, n):
    signature = pow(hash_int, d, n) # RSA digital signature generation formula.
    return signature

# Then this function verifies the signature 
def rsa_verify(signature, e, n):
    recovered_hash = pow(signature, e, n)
    return recovered_hash