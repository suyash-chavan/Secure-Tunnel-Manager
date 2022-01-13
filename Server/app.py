import requests
from flask import Flask, make_response, jsonify, request
import time
import json
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import hashlib
import socket

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI")
print(MONGO_URI)

AUTHORIZED_KEYS_PATH = "~/.ssh/authorized_keys"

store = pymongo.MongoClient(MONGO_URI)["watchman"]

def getFreePort():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]

@app.route('/')
def check():
    return 'WATCHMAN on duty sir!'

@app.route('/client/register', methods = ['POST'])
def ClientRegister():
    json_data = request.json

    dublicateClient = store["clients"].find({},{"clientKeyHash": hashlib.sha256(json_data["clientKey"].encode())})

    if(len(dublicateClient)!=0):
        return make_response(jsonify({
            "clientId": dublicateClient[0]._id,
            "clientDedicatedPort": dublicateClient[0].clientDedicatedPort
        }), 401)

    dedicatedPort = getFreePort()

    newClient = store["clients"].insert_one({
        "clientName": json_data["clientName"],
        "clientKeyHash": hashlib.sha256(json_data["clientKey"].encode()),
        "clientDedicatedPort": dedicatedPort
    })

    return make_response(jsonify({
            "clientId": newClient.inserted_id,
            "clientDedicatedPort": dedicatedPort
    }), 200)

@app.route('/client/awake', methods = ['POST'])
def clientAwake():
    reqData = json.loads(request.data)

    client = store["clients"].find({
        "clientName": reqData["clientName"],
        "clientKeyHash" : hashlib.sha256(reqData["clientKey"].encode())
    })

    if(len(client)==0):
        return make_response(jsonify({
            "status": "Client not found!"
        }), 401)

    client["clientData"].insert_one({
        "application": reqData["application"],
        "timestamp": time.time() * 1000,
        "data": reqData["data"]
    });

    return make_response(jsonify({
            "status": "Success"
        }), 200)

@app.route('/dashboard/applications', methods = ['GET'])
def listApplications():

    applications = []

    for app in store["applications"].find():
        applications.append({"applicationName": app["applicationName"], "applicationId": str(app["_id"])})

    return make_response(jsonify({
            "applications": applications,
            "status": "Success"
        }), 200)

@app.route('/dashboard/clients', methods = ['GET'])
def listClients():

    applicationId = json.loads(request.data)["applicationId"]
    clients = []

    for appClientId in store["applications"].find_one({ "_id": ObjectId(applicationId)})["clients"]:
        client = store["clients"].find_one({ "_id": ObjectId(appClientId)})
        clients.append({"clientName": client["clientName"], "clientId": str(client["_id"])})

    return make_response(jsonify({
            "clients": clients,
            "status": "Success"
        }), 200)

if __name__ == '__main__':
    app.run(port=8080)