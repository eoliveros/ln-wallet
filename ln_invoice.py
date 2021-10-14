"""
A class object that will be called on certain lightning-related endpoints
"""
from pyln.client import LightningRpc
import random

class LightningInstance():
    def __init__(self):
        self.instance = LightningRpc("/var/lib/docker/volumes/ln-wallet_clightning_bitcoin_datadir/_data/lightning-rpc")

    def get_info():
        return self.instance.getinfo()

    def create_invoice(self, amount, msg):
        return self.instance.invoice(amount, "lbl{}".format(random.random()), msg)

