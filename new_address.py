import secrets
import hashlib

from bitcoin.wallet import CBitcoinSecret, P2WPKHBitcoinAddress
from bitcoin.core import Hash160
from bitcoin.core.script import CScript, OP_0

def generate_wallet():
    h = secrets.token_bytes(32)
    seckey = CBitcoinSecret.from_secret_bytes(h)

    # Create an address from that private key.
    public_key = seckey.pub
    scriptPubKey = CScript([OP_0, Hash160(public_key)])
    return str(P2WPKHBitcoinAddress.from_scriptPubKey(scriptPubKey))
