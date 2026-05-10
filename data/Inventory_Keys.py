# data/Inventory_Keys.py
# Stores the pre-computed RSA key pairs for all 4 inventory nodes (A, B, C, D).
# Values of p, q, and e are fixed by the assignment — this file derives n, phi,
# and d from them using generate_rsa_values() in crypto_utils.py.
# Used by main.py (CLI) for signing and verifying inventory records.

import sys
import os

# Allow importing crypto_utils from the parent directory when running this file directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_utils import generate_rsa_values

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
