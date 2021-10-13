"""
Script will execute after form on /payment_form endpoint has been submitted
Code grabbed from https://bitcoin.stackexchange.com/questions/24571/how-to-make-a-simple-payment-with-the-python-bitcoinlib
Will change later
"""

from bitcointx.core import coins_to_satoshi, b2lx

import utils

rpc = utils.bitcoind_rpc()

print(rpc.getnetworkinfo())

addr = '1JwSSubhmg6iPtRjtyqhUYYH7bZg3Lfy1T' # TODO - this is not a testnet address
txid = rpc.sendtoaddress(addr, coins_to_satoshi(0.001))
print(b2lx(txid))


