from flask import (
    Blueprint,
    request,
    make_response,
    jsonify)

import socket
import hashlib
import time
from bson.objectid import ObjectId

from watchman.blueprints.database.mongodb import store

clientRoutes = Blueprint('client', __name__)
AUTHORIZED_KEYS_PATH = "/home/iot/.ssh/authorized_keys"

def getFreePort():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]

@clientRoutes.route('/client/register', methods = ['POST'])
def clientRegister():
    json_data = request.json

    f = open(AUTHORIZED_KEYS_PATH, "a")
    f.write(json_data["clientKey"]+"\n")
    f.close()

    dublicateClient = store["clients"].find_one({"clientKeyHash": hashlib.sha256(json_data["clientKey"].encode()).hexdigest()})

    if(dublicateClient!=None):
        return make_response(jsonify({
            "clientId": str(dublicateClient["_id"]),
            "clientDedicatedPort": dublicateClient["clientDedicatedPort"]
        }), 401)

    isPortFree = False
    dedicatedPort = 0

    while(not isPortFree):
        dedicatedPort = getFreePort()
        dublicateClient = store["clients"].find_one({"clientDedicatedPort": dedicatedPort})

        if(dublicateClient==None):
            isPortFree = True

    newClient = store["clients"].insert_one({
        "clientName": json_data["clientName"],
        "clientKeyHash": hashlib.sha256(json_data["clientKey"].encode()).hexdigest(),
        "clientDedicatedPort": dedicatedPort,
        "clientPassword": json_data["clientPassword"],
        "clientData": {},
        "clientMetrics": {}
    })

    return make_response(jsonify({
            "clientId": str(newClient.inserted_id),
            "clientDedicatedPort": dedicatedPort
    }), 200)

@clientRoutes.route('/client/awake', methods = ['POST'])
def clientAwake():
    reqData = request.json

    clientId = reqData["clientId"]
    clientKey = reqData["clientKey"]

    client = store["clients"].find_one({"clientKeyHash": hashlib.sha256(clientKey.encode()).hexdigest()})


    if(client==None):
        return make_response(jsonify({
            "status": "Client not found!"
        }), 401)

    store["clients"].update_one({ "_id": ObjectId(clientId)}, {"$push": { "clientData."+"awake" :{ "timestamp": round(time.time() * 1000)} } } )

    return make_response(jsonify({
            "status": "Success"
        }), 200)


@clientRoutes.route('/client/metrics', methods = ['POST'])
def pushMetrics():
    appId = request.json["applicationId"]
    clientId = request.json["clientId"]

    store["clients"].update_one({ "_id": ObjectId(clientId)}, { "$set": { "clientMetrics."+appId: request.json["metrics"] } } )

    return make_response(jsonify({
            "status": "Success"
        }), 200)


@clientRoutes.route('/client/data', methods = ['POST'])
def pushData():
    appId = request.json["applicationId"]
    clientId = request.json["clientId"]

    data = request.json["data"]

    data["timestamp"] = round(time.time() * 1000)

    store["clients"].update_one({ "_id": ObjectId(clientId)}, {"$push": { "clientData."+appId : data } } )

    return make_response(jsonify({
            "status": "Success"
        }), 200)
