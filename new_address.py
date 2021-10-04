import hashlib

from bitcoin.wallet import CBitcoinSecret, P2WPKHBitcoinAddress

def generate_wallet():
    # Create the (in)famous correct brainwallet secret key.
    h = hashlib.sha256(b'correct horse battery staple').digest()
    seckey = CBitcoinSecret.from_secret_bytes(h)

    # Create an address from that private key.
    public_key = seckey.pub
    scriptPubKey = CScript([OP_0, Hash160(public_key)])
    return P2WPKHBitcoinAddress.from_scriptPubKey(scriptPubKey)
