from flask import Flask, render_template, request, redirect
from flask_cors import CORS
from new_address import *

app = Flask(__name__)
CORS(app)


@app.route('/payment_form')
def payment_form():
    return render_template("payment_form.html")

@app.route('/new_address')
def new_address():
    return render_template("new_address.html", address=generate_wallet())

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
