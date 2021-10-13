import os

import bitcointx.rpc

def bitcoind_rpc():
    if 'SERVICE_URL' in os.environ:
        return bitcointx.rpc.RPCCaller(service_url=os.environ['SERVICE_URL'])
    return bitcointx.rpc.RPCCaller(conf_file='bitcoin.conf')
