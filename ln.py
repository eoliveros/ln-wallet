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
        # create a LN invoice
        return self.instance.invoice(amount, "lbl{}".format(random.random()), msg)

    def send_invoice(self, bolt11):
        # pay a bolt11 invoice
        return self.instance.pay(bolt11)

    def payment_status(self, bolt11string):
        # show the status of a specific paid bolt11 invoice
        return self.instance.listpays(bolt11=bolt11string)

    def list_paid(self):
        # show the status of all paid bolt11 invoice
        return self.instance.listpays()

    def open_channel(self, node_id, amount):
        return self.instance.fundchannel_start(node_id, amount)
