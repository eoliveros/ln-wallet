import bitcointx.rpc

def bitcoind_rpc():
    return bitcointx.rpc.RPCCaller(conf_file='bitcoin.conf')
