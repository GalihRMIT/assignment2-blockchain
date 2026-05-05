import hashlib
from math import gcd

def mod_inverse(e, phi):
    return pow(e, -1, phi)

# NOT CREATING RAMDOM KEYS but taking the given p, q, and e then calcualtes them to n, phi, and d
def generate_rsa_values(p, q, e):
    n = p * q #RSA key generation Formula
    phi = (p - 1) * (q - 1) # Euler's toient calculation

    if gcd(e, phi) != 1: # Check whether the GCD is 1 and if its not then e cannot be used to calculate the d
        raise ValueError("Invalid RSA Values: The e and phi are not coprime.")
    
    d = mod_inverse(e, phi)

    return {
        "p":p,  
        "q":q,
        "e":e,
        "n":n,
        "phi":phi,
        "d":d
    }

def record_to_string(record):
    return f"{record['item_id']},{record['quantity']},{record['price']},{record['location']}"

def hash_record(record):
    record_string = record_to_string(record)

    hash_hex = hashlib.sha256(record_string.encode()).hexdigest()
    hash_int = int(hash_hex, 16)

    return hash_hex, hash_int

def rsa_sign(hash_int, d, n):
    signature = pow(hash_int, d, n)
    return signature

def rsa_verify(signature, e, n):
    recovered_hash = pow(signature, e, n)
    return recovered_hash