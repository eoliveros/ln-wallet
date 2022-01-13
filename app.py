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

def check_nodes():
    ln_instance = LightningInstance()
    list_nodes = ln_instance.list_nodes()
    return list_nodes

@app.route('/')
def index():
    ln_instance = LightningInstance()
    funds_dict = ln_instance.list_funds()
    list_nodes = check_nodes()
    number_nodes = len(list_nodes["nodes"])
    if number_nodes < 1:
        ### ideas we could get the blockstream address and set it statically
        if os.getenv("NODE_ADDRESS"):
            ### ideas we could get the blockstream address and set it statically
            node_address = os.getenv("NODE_ADDRESS")
        ### testnet node
        else:
            node_address = '02312627fdf07fbdd7e5ddb136611bdde9b00d26821d14d94891395452f67af248@23.237.77.12:9735'
        try:
            ln_instance = LightningInstance()
            result = ln_instance.connect_nodes(node_address)
            #flash(Markup(f'successfully added node address: {node_address}'), 'success')
        except Exception as e:
            flash(Markup(e.args[0]), 'danger')
    return render_template("index.html", funds_dict=funds_dict)

@app.route('/lightningd_getinfo')
def lightningd_getinfo_ep():
    info = LightningInstance().get_info()
    return render_template('lightningd_getinfo.html', info=info)

@app.route('/send_bitcoin')
def send_bitcoin():
    ln_instance = LightningInstance()
    onchain = int(ln_instance.list_funds()["sats_onchain"]) / 100000000
    return render_template('send_bitcoin.html', bitcoin_explorer=app.config["BITCOIN_EXPLORER"], onchain=onchain)

@app.route('/create_psbt')
def create_psbt():
    ln_instance = LightningInstance()
    onchain = int(ln_instance.list_funds()["sats_onchain"]) / 100000000
    return render_template('create_psbt.html', bitcoin_explorer=app.config["BITCOIN_EXPLORER"], onchain=onchain)

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
    qrcode_svg = qrcode_svg_create_ln(bolt11)
    return render_template("create_invoice.html", bolt11=bolt11, qrcode_svg=qrcode_svg)

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

@app.route('/invoices', methods=['GET'])
def invoices():
    ln_instance = LightningInstance()
    paid_invoices = ln_instance.list_paid()
    return render_template("invoices.html", paid_invoices=paid_invoices)

@app.route('/channel_opener', methods=['GET'])
def channel_opener():
    return render_template("channel_opener.html")

@app.route('/open_channel/<string:node_pubkey>/<int:amount>', methods=['GET'])
def open_channel(node_pubkey, amount):
    ln_instance = LightningInstance()
    try:
        ln_instance.connect_nodes(node_pubkey)
        node_id = node_pubkey.split("@")
        result = ln_instance.fund_channel(node_id[0], amount)
        flash(Markup(f'successfully added node id: {node_id[0]} with the amount: {amount}'), 'success')
    except Exception as e:
        flash(Markup(e.args[0]), 'danger')
    return render_template("channel_opener.html")

@app.route('/list_peers', methods=['GET', 'POST'])
def list_peers():
    ln_instance = LightningInstance()
    if request.method == 'POST':
        oscid = request.form["oscid"]
        iscid = request.form["iscid"]
        sats = request.form["amount"]
        amount = str(int(sats) * 1000) +str('msat')
        try:
            ln_instance = LightningInstance()
            result = ln_instance.rebalance_individual_channel(oscid, iscid, amount)
            flash(Markup(f'successfully move funds from: {oscid} to: {iscid} with the amount: {sats}sats'), 'success')
        except Exception as e:
            flash(Markup(e.args[0]), 'danger')
    peers = ln_instance.list_peers()["peers"]
    for i in range(len(peers)):
        peers[i]["sats_total"] = 0
        peers[i]["can_send"] = 0
        peers[i]["can_receive"] = 0
        peers[i]["scid"] = ""
        # I'm assuming there will only be one channel for each node, but I'm using an array in case there's more
        peers[i]["channel_states"] = []
        for channel in peers[i]["channels"]:
            if channel["state"] == 'CHANNELD_NORMAL':
                peers[i]["sats_total"] += int(channel["msatoshi_total"])/1000
                peers[i]["can_send"] += int(channel["msatoshi_to_us"])/1000
                peers[i]["can_receive"] += int(channel["out_msatoshi_fulfilled"])/1000
                for scid in channel["short_channel_id"]:
                    peers[i]["scid"] += scid
                peers[i]["channel_states"].append(channel["state"])

        # round as a last step, for accuracy
        peers[i]["sats_total"] = int(peers[i]["sats_total"])
        peers[i]["can_send"] = int(peers[i]["can_send"])
        peers[i]["can_receive"] = int(peers[i]["can_receive"])
    return render_template("list_peers.html", peers=peers)

@app.route('/list_nodes')
def list_nodes():
    ln_instance = LightningInstance()
    list_nodes = ln_instance.list_nodes()
    return list_nodes

@app.route('/list_channels')
def list_channels():
    ln_instance = LightningInstance()
    list_channels = ln_instance.list_channels()
    return list_channels

@app.route('/close/<string:peer_id>')
def close(peer_id):
    ln_instance = LightningInstance()
    close_tx = ln_instance.close_channel(peer_id)
    return render_template("close.html", close_tx=close_tx, bitcoin_explorer=app.config["BITCOIN_EXPLORER"])


@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    ln_instance = LightningInstance()
    outputs_dict = request.json["address_amount"]
    try:
        tx_result = ln_instance.multi_withdraw(outputs_dict)
    except:
        tx_result = "error"
    return tx_result

@app.route('/psbt', methods=['GET', 'POST'])
def psbt():
    ln_instance = LightningInstance()
    outputs_dict = request.json["address_amount"]
    try:
        tx_result = ln_instance.prepare_psbt(outputs_dict)
    except Exception as e:
        tx_result = str(e)
    return tx_result

@app.route('/broadcast')
def broadcast():
    ln_instance = LightningInstance()
    return render_template('broadcast.html', bitcoin_explorer=app.config["BITCOIN_EXPLORER"])

@app.route('/send_psbt', methods=['GET', 'POST'])
def send_psbt():
    ln_instance = LightningInstance()
    outputs_dict = request.json["signed_psbt"]
    try:
        tx_result = ln_instance.send_psbt(outputs_dict)
    except Exception as e:
        tx_result = str(e)
    return tx_result

@app.route('/sign')
def sign():
    ln_instance = LightningInstance()
    return render_template('sign.html', bitcoin_explorer=app.config["BITCOIN_EXPLORER"])

@app.route('/sign_psbt', methods=['GET', 'POST'])
def sign_psbt():
    ln_instance = LightningInstance()
    outputs_dict = request.json["unsigned_psbt"]
    try:
        tx_result = ln_instance.sign_psbt(outputs_dict)
    except Exception as e:
        tx_result = str(e)
    return tx_result

@app.route('/status/<string:bolt11>')
def get_status(bolt11):
    ln_instance = LightningInstance()
    status = ln_instance.payment_status(bolt11)
    return render_template("status.html", status=status)

@app.route('/decode_pay', strict_slashes=False)
@app.route('/decode_pay/<bolt11>', strict_slashes=False)
def decode_pay(bolt11=None):
    if bolt11 is None:
        return "Please enter a non-empty bolt11 string"
    try:
        ln_instance = LightningInstance()
        return ln_instance.decode_pay(str(bolt11))
    except Exception as e:
        return str(e)
    return "Something went wrong"

@app.route('/waitany')
def wait_any():
    # for testing
    ln_instance = LightningInstance()
    return ln_instance.wait_any()

@app.route('/get_fee')
def get_fee():
    ln_instance = LightningInstance()
    return ln_instance.fee_rates()

@app.route('/send_node')
def send_node():
    return render_template("send_node.html")

@app.route('/keysend', strict_slashes=False)
@app.route('/keysend/<node_id>', strict_slashes=False)
@app.route('/keysend/<node_id>/<sats>', strict_slashes=False)
def key_send(node_id=None, sats=None):
    if (node_id is None) or (sats is None):
        return "Please check that node_id or sats is not empty"
    elif ("@" in str(node_id)) or (":" in str(node_id)):
        return "Please enter just the node pubkey, NOT pubkey@ip:protocol"
    else:
        try:
            ln_instance = LightningInstance()
            return ln_instance.key_send(str(node_id), int(sats)*1000)
        except ValueError:
            return "Please check that sats is a valid integer"
        except Exception as e:
            return str(e)
    return "Something went wrong"

@app.route('/list_forwards')
def list_forwards():
    ln_instance = LightningInstance()
    return ln_instance.list_forwards()


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
