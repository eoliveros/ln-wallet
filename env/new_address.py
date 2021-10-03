from bitcoinlib.wallets import Wallet

def generate_wallet():
    w = Wallet.create('wallet_segwit_p2wpkh', witness_type='segwit')
    return w.get_key().address
