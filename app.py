import os

from flask import Flask, render_template, request, redirect, flash, Markup
from flask_cors import CORS

import utils
from new_address import new_address
from ln import LightningInstance

app = Flask(__name__)
CORS(app)

if os.getenv("SECRET_KEY"):
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if os.getenv("BITCOIN_EXPLORER"):
    app.config["BITCOIN_EXPLORER"] = os.getenv("BITCOIN_EXPLORER")
else:
    app.config["BITCOIN_EXPLORER"] = "https://testnet.bitcoinexplorer.org/tx"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/bitcoind_getnetworkinfo')
def bitcoind_getnetworkinfo_ep():
    return str(utils.bitcoind_rpc().getnetworkinfo())

@app.route('/bitcoind_getwalletinfo')
def bitcoind_getwalletinfo_ep():
    return str(utils.bitcoind_rpc().getwalletinfo())

@app.route('/bitcoind_getaddressesbylabel')
def bitcoind_getaddressesbylabel_ep():
    wallet_details = utils.bitcoind_rpc().getwalletinfo()
    wallet_name = wallet_details["walletname"]
    addresses = utils.bitcoind_rpc().getaddressesbylabel(f'{wallet_name}')
    print(list(addresses.keys()))
    print(addresses)
    for addr in list(addresses.keys()):
        return addr

@app.route('/bitcoind_getnewaddress')
def bitcoind_getnewaddress_ep():
    wallet_details = utils.bitcoind_rpc().getwalletinfo()
    wallet_name = wallet_details["walletname"]
    address = utils.bitcoind_rpc().getnewaddress(f'{wallet_name}')
    return render_template("bitcoin_address.html", address=address)

@app.route('/bitcoind_getbalance')
def bitcoind_getbalance_ep():
    return str(utils.bitcoind_rpc().getbalance())

@app.route('/lightningd_getinfo')
def lightningd_getinfo_ep():
    info = LightningInstance().get_info()
    return str(info)

@app.route('/send_form', methods=['GET', 'POST'])
def send_form():
    if request.method == 'POST':
        address = request.form['address']
        amount = request.form['amount']
        message = request.form['message']
        try:
            bitcoin_explorer = app.config["BITCOIN_EXPLORER"]
            txid = utils.bitcoind_rpc().sendtoaddress(address, amount)
            flash(Markup(f'<a href="{bitcoin_explorer}/{txid}">Transaction ID: {txid}</a>'), 'success')
        except Exception as e:
            flash(Markup(e.args[0]['message']), "danger")
    return render_template("send_form.html")

@app.route('/new_address')
def new_address_ep():
    address = new_address()
    return render_template("new_address.html", address=address)

@app.route('/ln_invoice', methods=['GET'])
def ln_invoice():
    return render_template("ln_invoice.html")

@app.route('/create_invoice/<int:amount>/<string:message>/')
def create_invoice(amount, message):
    ln_instance = LightningInstance()
    bolt11 = ln_instance.create_invoice(amount, message)["bolt11"]
    return render_template("create_invoice.html", bolt11=bolt11)


if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
