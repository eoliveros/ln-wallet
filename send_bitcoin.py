"""
Script will execute after form on /payment_form endpoint has been submitted
Code grabbed from https://bitcoin.stackexchange.com/questions/24571/how-to-make-a-simple-payment-with-the-python-bitcoinlib
Will change later
"""

from bitcoin.core import COIN, b2lx
import bitcoin.wallet
import bitcoin.rpc
try:
    # This moved between versions
    from bitcoin.base58 import CBitcoinAddress
except:
    from bitcoin.wallet import CBitcoinAddress

rpc = bitcoin.rpc.Proxy()
addr = CBitcoinAddress('1JwSSubhmg6iPtRjtyqhUYYH7bZg3Lfy1T')

txid = rpc.sendtoaddress(addr, 0.001 * COIN)
print(b2lx(txid))


