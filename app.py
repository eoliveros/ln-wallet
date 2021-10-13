import os

from flask import Flask, render_template, request, redirect, flash, Markup
from flask_cors import CORS

import utils
from new_address import new_address
from bitcoin_script import sending_bitcoin

app = Flask(__name__)
CORS(app)

if os.getenv("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

@app.route('/')
def index():
    return '<a href="/bitcoind_getnetworkinfo">bitcoind getnetworkinfo</a><br><a href="/bitcoind_getwalletinfo">bitcoind getwalletinfo</a><br><a href="/lightningd_getinfo">lightningd getinfo</a>'

@app.route('/bitcoind_getnetworkinfo')
def bitcoind_getnetworkinfo_ep():
    return str(utils.bitcoind_rpc().getnetworkinfo())

@app.route('/bitcoind_getwalletinfo')
def bitcoind_getwalletinfo_ep():
    return str(utils.bitcoind_rpc().getwalletinfo())

@app.route('/bitcoind_getwalletinfo')
def bitcoind_getinfo_ep():
    return utils.bitcoind_rpc().getwalletinfo()

@app.route('/lightningd_getinfo')
def lightningd_getinfo_ep():
    return 'not implemented'

@app.route('/payment_form', methods=['GET', 'POST'])
def payment_form_ep():
    if request.method == 'POST':
        address = request.form['address']
        amount = request.form['amount']
        message = request.form['message']
        try:
            txid = utils.bitcoind_rpc().sendtoaddress(address, amount)
            flash(Markup(f'<a href="https://testnet.bitcoinexplorer.org/tx/{txid}">Transaction ID: {txid}</a>'), 'success')
        except Exception as e:
            flash(Markup(e.args[0]['message']), "danger")
    return render_template("payment_form.html")

@app.route('/new_address')
def new_address_ep():
    address = new_address()
    return render_template("new_address.html", address=address)

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
