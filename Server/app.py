import requests
from flask import Flask
import json
import pymongo
import os
import hashlib
import socket

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")
AUTHORIZED_KEYS_PATH = "~/.ssh/authorized_keys"

watchman = pymongo.MongoClient(MONGO_URI)

@app.route('/')
def check():
    return 'WATCHMAN on duty sir!'

@app.route('/awake', methods = ['POST'])
def awake():
    json_data = request.json

    # json_data = {
    #   device name,
    #   device id or ssh key,
    # }

    data = {}

    # data = {
    #   device id,
    #   dedicated port
    # }

    return data

@app.route('/register', methods = ['POST'])
def register():
    json_data = request.json

    # json_data = {
    #   device name,
    #   ssh public key
    # }

    sock = socket.socket()
    sock.bind(('', 0))

    # Register Device in Database
    record = watchman.clients.insert_one({
        "clientName": json_data.deviceName,
        "clientKey": json_data.deviceKey,
        "keyHash": hashlib.sha256(json_data.deviceKey.encode()),
        "dedicatedPort": sock.getsockname()[1]
    })

    data = {
        "clientId": record.inserted_id,
        "dedicatedPort": sock.getsockname()[1]
    }

    return data