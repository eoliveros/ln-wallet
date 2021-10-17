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
    def send_invoice(self, bolt11):
        # so far just returns a decoded bolt11
        decoded_bolt11 = self.instance.decodepay(bolt11)
        route = self.instance.getroute(decoded_bolt11["routes"][0][0]["pubkey"], decoded_bolt11["msatoshi"], 1)
        return self.instance.sendpay(route["route"], decoded_bolt11["payment_hash"])
        #return decoded_bolt11
