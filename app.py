import os
import json
import qrcode
import qrcode.image.svg
import io

from flask import Flask, render_template, request, redirect, flash, Markup, url_for, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit


from ln import LightningInstance

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

if os.getenv("SECRET_KEY"):
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if os.getenv("BITCOIN_EXPLORER"):
    app.config["BITCOIN_EXPLORER"] = os.getenv("BITCOIN_EXPLORER")
else:
    app.config["BITCOIN_EXPLORER"] = "https://testnet.bitcoinexplorer.org"

def qrcode_svg_create(data):
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(data, image_factory=factory, box_size=35)
    output = io.BytesIO()
    img.save(output)
    svg = output.getvalue().decode('utf-8')
    return svg

def qrcode_svg_create_ln(data):
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(data, image_factory=factory, box_size=10)
    output = io.BytesIO()
    img.save(output)
    svg = output.getvalue().decode('utf-8')
    return svg

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

@app.route('/new_lightningd_getinfo')
def new_lightningd_getinfo_ep():
    info = LightningInstance().get_info()
    return render_template('new_lightningd_getinfo.html', info=info)

@app.route('/new_send_bitcoin')
def new_send_bitcoin():
    return render_template('new_send_bitcoin.html', bitcoin_explorer=app.config["BITCOIN_EXPLORER"])

@app.route('/new_list_txs')
def new_list_txs():
    ln_instance = LightningInstance()
    transactions = ln_instance.list_txs()
    sorted_txs = sorted(transactions["transactions"], key=lambda d: d["blockheight"], reverse=True)
    for tx in transactions["transactions"]:
        for output in tx["outputs"]:
            output["sats"] = int(output["msat"] / 1000)
            output.update({"sats": str(output["sats"])+" satoshi"})
    return render_template("new_list_transactions.html", transactions=sorted_txs, bitcoin_explorer=app.config["BITCOIN_EXPLORER"])

@app.route('/new_new_address')
def new_new_address_ep():
    ln_instance = LightningInstance()
    address = ln_instance.new_address()
    return render_template("new_new_address.html", address=address)

@app.route('/new_ln_invoice', methods=['GET'])
def new_ln_invoice():
    return render_template("new_ln_invoice.html")

@app.route('/new_create_invoice/<int:amount>/<string:message>/')
def new_create_invoice(amount, message):
    ln_instance = LightningInstance()
    bolt11 = ln_instance.create_invoice(int(amount*1000), message)["bolt11"]
    qrcode_svg = qrcode_svg_create_ln(bolt11)
    return render_template("new_create_invoice.html", bolt11=bolt11, qrcode_svg=qrcode_svg)

@app.route('/new_pay_invoice', methods=['GET'])
def new_pay_invoice():
    return render_template("new_pay_invoice.html")

@app.route('/new_pay/<string:bolt11>')
def new_pay(bolt11):
    ln_instance = LightningInstance()
    try:
        invoice_result = ln_instance.send_invoice(bolt11)
        return render_template("new_pay.html", invoice_result=invoice_result)
    except:
        return redirect(url_for("new_pay_error"))

@app.route('/new_pay_error')
def new_pay_error():
    return render_template("new_pay_error.html")

@app.route('/new_invoices', methods=['GET'])
def new_invoices():
    ln_instance = LightningInstance()
    paid_invoices = ln_instance.new_list_paid()
    return render_template("new_invoices.html", paid_invoices=paid_invoices)

@app.route('/new_channel_opener', methods=['GET'])
def new_channel_opener():
    return render_template("new_channel_opener.html")

@app.route('/new_open_channel/<string:node_id>/<int:amount>', methods=['GET'])
def new_open_channel(node_id, amount):
    ln_instance = LightningInstance()
    try:
        result = ln_instance.new_fund_channel(node_id, amount)
        flash(Markup(f'successfully added node id: {node_id}'), 'success')
    except Exception as e:
        flash(Markup(e.args[0]), 'danger')
    return render_template("new_channel_opener.html")

@app.route('/new_list_peers')
def new_list_peers():
    ln_instance = LightningInstance()
    peers = ln_instance.list_peers()["peers"]
    for peer in peers:
        print(peer)
        for channel in peer["channels"]:
    #        print(channel)
    #        print(type(channel))
    #        print(channel["funding"])
    #        print('local amount fund(msat): '+str(channel["funding"]["local_msat"]))
    #        print('remote amount fund(msat): '+str(channel["funding"]["remote_msat"]))
            channel_satoshi_total = int(channel["msatoshi_total"])
            channel_msatoshi_to_us = int(channel["msatoshi_to_us"])
            channel["channel_remote_msatoshi"] = int(channel_satoshi_total - channel_msatoshi_to_us)
        print(peer)
    #print('::')
    return render_template("new_list_peers.html", peers=peers)

@app.route('/new_list_nodes')
def new_list_nodes():
    ln_instance = LightningInstance()
    list_nodes = ln_instance.new_list_nodes()
    return list_nodes

@app.route('/new_node_connector')
def new_node_connector():
    return render_template("new_node_connector.html")

@app.route('/new_connect_nodes/<string:node_address>')
def new_connect_nodes(node_address):
    ln_instance = LightningInstance()
    try:
        result = ln_instance.new_connect_nodes(node_address)
        flash(Markup(f'successfully added node address: {node_address}'), 'success')
    except Exception as e:
        flash(Markup(e.args[0]), 'danger')
    return render_template("new_node_connector.html")

@app.route('/new_list_channels')
def new_list_channels():
    ln_instance = LightningInstance()
    list_channels = ln_instance.list_channels()
    return list_channels
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
    bolt11 = ln_instance.create_invoice(int(amount*1000), message)["bolt11"]
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
    return decodedpay

@app.route('/waitany')
def wait_any():
    # for testing
    ln_instance = LightningInstance()
    return ln_instance.wait_any()

'''
socket-io notifications
'''

@socketio.on('connect')
def test_connect(auth):
    print("Client connected")

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('waitany')
def wait_any_invoice():
    print('client called recieveany')
    ln_instance = LightningInstance()
    res = ln_instance.wait_any()
    emit('invoice', {'data': res})



if __name__=='__main__':
    flask_debug = 'DEBUG' in os.environ
    app.secret_key = os.urandom(256)
    app.run(host='0.0.0.0', debug=flask_debug, port=5000)
    socketio.run(app)
