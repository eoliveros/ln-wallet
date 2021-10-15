"""
A class object that will be called on certain lightning-related endpoints
"""
import os
import random

from pyln.client import LightningRpc

class LightningInstance():
    def __init__(self):
        if 'RPC_FILE' in os.environ:
            self.instance = LightningRpc(os.environ['RPC_FILE'])
        else:
            self.instance = LightningRpc("/etc/lightning/lightning-rpc")

    def get_info(self):
        return self.instance.getinfo()

    def create_invoice(self, amount, msg):
        return self.instance.invoice(amount, "lbl{}".format(random.random()), msg)

