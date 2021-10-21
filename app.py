import os
import json

from flask import Flask, render_template, request, redirect, flash, Markup
from flask_cors import CORS

import utils
from ln import LightningInstance

app = Flask(__name__)
CORS(app)

if os.getenv("SECRET_KEY"):
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if os.getenv("BITCOIN_EXPLORER"):
    app.config["BITCOIN_EXPLORER"] = os.getenv("BITCOIN_EXPLORER")
else:
    app.config["BITCOIN_EXPLORER"] = "https://testnet.bitcoinexplorer.org"

def bitcoind_getbalance_ep():
    return str(utils.bitcoind_rpc().getbalance())

@app.route('/')
def index():
    return render_template("index.html", btc_balance=bitcoind_getbalance_ep())

@app.route('/list_txs')
def list_txs():
    ln_instance = LightningInstance()
    transactions = ln_instance.list_txs()
    sorted_txs = sorted(transactions["transactions"], key=lambda d: d["blockheight"], reverse=True)
    return render_template("list_transactions.html", transactions=sorted_txs, bitcoin_explorer=app.config["BITCOIN_EXPLORER"])


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

@app.route('/lightningd_getinfo')
def lightningd_getinfo_ep():
    info = LightningInstance().get_info()
    return str(info)

@app.route('/send_form', methods=['GET', 'POST'])
def send_form():
    if request.method == 'POST':
        address = str(request.form['address'])
        amount = request.form['amount']
        message = request.form['message']
        address_amount = f"{{\"{address}\": {amount}}}"
        try:
            bitcoin_explorer = app.config["BITCOIN_EXPLORER"]
            txid = utils.bitcoind_rpc().sendtoaddress(address, amount)
            ### CAN USE SENDMANY(BELOW) OR SENDTOADDRESS(ABOVE)
            #txid = utils.bitcoind_rpc().sendmany("", json.loads(address_amount))
            flash(Markup(f'<a href="{bitcoin_explorer}/{txid}">Transaction ID: {txid}</a>'), 'success')
        except Exception as e:
            flash(Markup(e.args[0]['message']), "danger")
    return render_template("send_form.html")

@app.route('/send_multiple', methods=['GET', 'POST'])
def send_multiple():
    if request.method == 'POST':
        try:
            bitcoin_explorer = app.config["BITCOIN_EXPLORER"]
            txid = utils.bitcoind_rpc().sendmany("", json.loads(request.form['address_amount']))
            flash(Markup(f'<a href="{bitcoin_explorer}/{txid}">Transaction ID: {txid}</a>'), 'success')
        except Exception as e:
            flash(Markup(e.args[0]['message']), "danger")
    return render_template('send_multiple.html')

@app.route('/new_address')
def new_address_ep():
    ln_instance = LightningInstance()
    address = ln_instance.new_address()
    return render_template("new_address.html", address=address)

@app.route('/ln_invoice', methods=['GET'])
def ln_invoice():
    return render_template("ln_invoice.html")

@app.route('/create_invoice/<int:amount>/<string:message>/')
def create_invoice(amount, message):
    ln_instance = LightningInstance()
    bolt11 = ln_instance.create_invoice(amount, message)["bolt11"]
    return render_template("create_invoice.html", bolt11=bolt11)

@app.route('/pay_invoice', methods=['GET'])
def pay_invoice():
    return render_template("pay_invoice.html")

@app.route('/pay/<string:bolt11>')
def pay(bolt11):
    ln_instance = LightningInstance()
    sent_invoice = ln_instance.send_invoice(bolt11)
    return render_template("pay.html", sent_invoice=sent_invoice)

@app.route('/status/<string:bolt11>')
def get_status(bolt11):
    ln_instance = LightningInstance()
    ln_instance.payment_status
    status = ln_instance.payment_status(bolt11)
    return render_template("status.html", status=status)

@app.route('/paid', methods=['GET'])
def paid():
    ln_instance = LightningInstance()
    paid_invoices = ln_instance.list_paid()
    return render_template("paid.html", paid_invoices=paid_invoices)

@app.route('/channel_opener', methods=['GET'])
def channel_opener():
    return render_template("channel_opener.html")

@app.route('/open_channel/<string:node_id>/<int:amount>', methods=['GET'])
def open_channel(node_id, amount):
    ln_instance = LightningInstance()
    return ln_instance.open_channel(node_id, amount)


if __name__=='__main__':
    flask_debug = 'DEBUG' in os.environ
    app.run(host='0.0.0.0', debug=flask_debug, port=5000)
