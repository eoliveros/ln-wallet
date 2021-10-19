# Lightning Network Wallet ⚡

* A development environment for Alloy's lightning wallet
* Currently in Testnet mode

# Requirements 🔧

* [Docker installed](https://docs.docker.com/get-docker/)
* [docker-compose installed](https://docs.docker.com/compose/install/)
* python3 installed
* pip installed: `sudo apt-get install python3-pip` on Linux
* vitualenv installed: `sudo pip3 install virtualenv` on Linux
* [python-bitcointx](https://pypi.org/project/python-bitcointx/)
* libsecp256k1 (`sudo apt-get install libsecp256k1-0` or https://github.com/cuber/homebrew-libsecp256k1 on mac)

# To run the docker images:

* `./build-docker-images.sh`
* `sudo docker-compose up`
* go to [`localhost`](http:/localhost) to see lightningd helper apps

# For running the Flask app:

* It is recommended to run the Flask app in a virtual environment
* `virtualenv venv`
* `source venv/bin/activate`
* `python3.8 -m pip install -r requirements.txt`
* `python app.py` 

# To stop:

* ctrl-c to stop Flask then `deactivate` to deactivate the venv


# Endpoints:

* `/payment_form` returns an html page for a payment invoice form
* `/new_address` returns an html page showing a generated bitcoin address
* `/ln_invoice` returns an html page for creating LN invoices
* `/pay_invoice` returns an html page for paying LN invoices
* `/pay/<bolt11>` pays a bolt11 invoice and returns an html page of the result
* `/paid` returns an html page of the status of all paid bolt11 invoices
* `/status/<bolt11>` returns an html page of the status of a specific bolt11 invoice payment


