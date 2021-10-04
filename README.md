# Lightning Network Wallet ⚡

* A development environment for Alloy's lightning wallet
* Currently in Testnet mode

# Requirements 🔧

* [Docker installed](https://docs.docker.com/get-docker/)
* [docker-compose installed](https://docs.docker.com/compose/install/)
* python3 installed
* pip installed: `sudo apt-get install python3-pip` on Linux
* vitualenv installed: `sudo pip3 install virtualenv` on Linux
* [python-bitcoinlib requirements](https://pypi.org/project/python-bitcoinlib/)

# To run docker lightning network image:

* run `sudo docker-compose up`

# For running the Flask app:

* It is recommended to run the Flask app in a virtual environment
* `virtualenv venv`
* `cd env && source bin/activate`
* `python3.8 -m pip install -r requirements.txt`
*  `flask run` 

# To stop:

* ctrl-c to stop Flask then `deactivate` to deactivate the venv


# Endpoints:

* `/payment_form` returns an html page for a payment invoice form
