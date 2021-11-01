import os
import json

from flask import Flask, render_template, request, redirect, flash, Markup, url_for
from flask_cors import CORS

from ln import LightningInstance

app = Flask(__name__)
CORS(app)

if os.getenv("SECRET_KEY"):
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if os.getenv("BITCOIN_EXPLORER"):
    app.config["BITCOIN_EXPLORER"] = os.getenv("BITCOIN_EXPLORER")
else:
    app.config["BITCOIN_EXPLORER"] = "https://testnet.bitcoinexplorer.org"

@app.route('/')
def index():
    ln_instance = LightningInstance()
    funds_dict = ln_instance.list_funds()
    return render_template("index.html", funds_dict=funds_dict)

### ERICK trying to create a new layout with bootstrap.
@app.route('/new_index')
def new_index():
    ln_instance = LightningInstance()
    funds_dict = ln_instance.list_funds()
    return render_template("new_index.html", funds_dict=funds_dict)

@app.route('/new_send_bitcoin')
def new_send_bitcoin():
    return render_template('new_send_bitcoin.html', bitcoin_explorer=app.config["BITCOIN_EXPLORER"])
###

@app.route('/list_txs')
def list_txs():
    ln_instance = LightningInstance()
    transactions = ln_instance.list_txs()
    sorted_txs = sorted(transactions["transactions"], key=lambda d: d["blockheight"], reverse=True)
    for tx in transactions["transactions"]:
        for output in tx["outputs"]:
            output["sats"] = int(output["msat"] / 1000)
            output.update({"sats": str(output["sats"])+" satoshi"})
    return render_template("list_transactions.html", transactions=sorted_txs, bitcoin_explorer=app.config["BITCOIN_EXPLORER"])

@app.route('/list_peers')
def list_channels():
    ln_instance = LightningInstance()
    peers = ln_instance.list_peers()["peers"]
    return render_template("list_peers.html", peers = peers)

@app.route('/lightningd_getinfo')
def lightningd_getinfo_ep():
    info = LightningInstance().get_info()
    return str(info)

@app.route('/send_bitcoin')
def send_bitcoin():
    return render_template('send_bitcoin.html', bitcoin_explorer=app.config["BITCOIN_EXPLORER"])

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    ln_instance = LightningInstance()
    outputs_dict = request.json["address_amount"]
    try:
        tx_result = ln_instance.multi_withdraw(outputs_dict)
    except:
        tx_result = "error"
    return tx_result

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
    try:
        invoice_result = ln_instance.send_invoice(bolt11)
        return render_template("pay.html", invoice_result=invoice_result)
    except:
        return redirect(url_for("pay_error"))

@app.route('/pay_error')
def pay_error():
    return render_template("pay_error.html")

@app.route('/status/<string:bolt11>')
def get_status(bolt11):
    ln_instance = LightningInstance()
    status = ln_instance.payment_status(bolt11)
    return render_template("status.html", status=status)

@app.route('/invoices', methods=['GET'])
def invoices():
    ln_instance = LightningInstance()
    paid_invoices = ln_instance.list_paid()
    return render_template("invoices.html", paid_invoices=paid_invoices)

@app.route('/channel_opener', methods=['GET'])
def channel_opener():
    return render_template("channel_opener.html")

@app.route('/open_channel/<string:node_id>/<int:amount>', methods=['GET'])
def open_channel(node_id, amount):
    ln_instance = LightningInstance()
    return ln_instance.open_channel(node_id, amount)

@app.route('/decode_pay/<string:bolt11>')
def decode_pay(bolt11):
    ln_instance = LightningInstance()
    decodedpay = ln_instance.decode_pay(bolt11)
    #msat_string = request.json["amount_msat"]
    return decodedpay


if __name__=='__main__':
    flask_debug = 'DEBUG' in os.environ
    app.run(host='0.0.0.0', debug=flask_debug, port=5000)
