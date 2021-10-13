'''
This script will contain everything to do with the /new_address flask endpoint
'''

import utils

rpc = utils.bitcoind_rpc()

def new_address():
    return rpc.getnewaddress()

if __name__ == '__main__':
    print(new_address())
