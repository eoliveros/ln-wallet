'''
This script will contain everything to do with the /new_address flask endpoint
'''

import secrets
import hashlib

from bitcoin.wallet import CBitcoinSecret, P2WPKHBitcoinAddress
from bitcoin.core import Hash160
from bitcoin.core.script import CScript, OP_0


class NewWallet:

    def __init__(self):
        self.random_bytes = secrets.token_bytes(32)
        self.seckey = CBitcoinSecret.from_secret_bytes(self.random_bytes)
        # Create an address from that private key.
        self.public_key = self.seckey.pub
        self.scriptPubKey = CScript([OP_0, Hash160(self.public_key)])
        self.publicAddress = str(P2WPKHBitcoinAddress.from_scriptPubKey(self.scriptPubKey))
