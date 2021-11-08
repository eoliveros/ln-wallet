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
        invoice_result = self.instance.pay(bolt11)
        invoice_result["sats_sent"] = int(invoice_result["msatoshi_sent"] / 1000)
        return invoice_result

    def payment_status(self, bolt11string):
        # show the status of a specific paid bolt11 invoice
        return self.instance.listpays(bolt11=bolt11string)

    def list_paid(self):
        # show the status of all paid bolt11 invoice
        return self.instance.listpays()

    def list_peers(self):
        return self.instance.listpeers()

    def open_channel(self, node_id, amount):
        return self.instance.fundchannel_start(node_id, amount)

    def new_address(self):
        # return a bech32 address
        return self.instance.newaddr(addresstype='bech32')

    def list_txs(self):
        return self.instance.listtransactions()

    def multi_withdraw(self, outputs_dict):
        # outputs is in form {"address" : amount}
        return self.instance.multiwithdraw(outputs_dict)

    def list_funds(self):
        funds_dict = self.instance.listfunds()
        funds_channel = 0
        funds_onchain = 0
        for i in range(len(funds_dict["channels"])):
            funds_channel += int(str(funds_dict["channels"][i]["our_amount_msat"]).split("msat", 1)[0])
            sats_channel = int(funds_channel / 1000)

        for i in range(len(funds_dict["outputs"])):
            if funds_dict["outputs"][i]["status"] == "confirmed":
                funds_onchain += int(str(funds_dict["outputs"][i]["amount_msat"]).split("msat", 1)[0])
                sats_onchain = int(funds_onchain / 1000)

        return({"funds_channel" : funds_channel, "funds_onchain" : funds_onchain, "sats_channel" : sats_channel, "sats_onchain" : sats_onchain})

    def decode_pay(self, bolt11):
        bolt11_result = self.instance.decodepay(bolt11)
        amount_sats = int(int(str(bolt11_result["amount_msat"]).split("msat", 1)[0]) / 1000)
        return {"amount" : amount_sats, "description" : bolt11_result["description"], "payee" : bolt11_result["payee"] }
    
    def list_paid(self):
        invoice_list = self.instance.listinvoices()
        paid_list = []
        for i in range(len(invoice_list["invoices"])):
            current_invoice= invoice_list["invoices"][i]
            if current_invoice["status"] == "paid":
                paid_list.append(current_invoice)
        return paid_list

    def wait_any(self):
        invoice_list = self.list_paid()
        last_index = len(invoice_list)
        return self.instance.waitanyinvoice(lastpay_index=last_index)

