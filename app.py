from flask import Flask, render_template, request, redirect
from flask_cors import CORS

import utils
from new_address import new_address

app = Flask(__name__)
CORS(app)

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

@app.route('/payment_form')
def payment_form_ep():
    return render_template("payment_form.html")

@app.route('/new_address')
def new_address_ep():
    address = new_address()
    return render_template("new_address.html", address=address)

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
