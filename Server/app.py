from http import client
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
def clientRegister():
    json_data = request.json

    dublicateClient = store["clients"].find_one({"clientKeyHash": hashlib.sha256(json_data["clientKey"].encode()).hexdigest()})

    if(dublicateClient!=None):
        return make_response(jsonify({
            "clientId": str(dublicateClient["_id"]),
            "clientDedicatedPort": dublicateClient["clientDedicatedPort"]
        }), 401)

    dedicatedPort = getFreePort()

    newClient = store["clients"].insert_one({
        "clientName": json_data["clientName"],
        "clientKeyHash": hashlib.sha256(json_data["clientKey"].encode()).hexdigest(),
        "clientDedicatedPort": dedicatedPort,
        "clientData": {},
        "clientMetrics": {}
    })

    file1 = open(AUTHORIZED_KEYS_PATH, "a")
    file1.write(json_data["clientKey"]+"\n")
    file1.close()

    return make_response(jsonify({
            "clientId": str(newClient.inserted_id),
            "clientDedicatedPort": dedicatedPort
    }), 200)

@app.route('/client/awake', methods = ['POST'])
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

@app.route('/dashboard/applications', methods = ['GET'])
def listApplications():

    applications = []

    for app in store["applications"].find():
        applications.append({"applicationName": app["applicationName"], "applicationId": str(app["_id"])})

    return make_response(jsonify({
            "applications": applications,
            "status": "Success"
        }), 200)

@app.route('/dashboard/clients', methods = ['POST'])
def listClients():
    applicationId = request.json["applicationId"]
    clients = []

    for appClientId in store["applications"].find_one({ "_id": ObjectId(applicationId)})["clients"]:
        client = store["clients"].find_one({ "_id": ObjectId(appClientId)})
        clients.append({"clientName": client["clientName"], "clientId": str(client["_id"])})

    return make_response(jsonify({
            "clients": clients,
            "status": "Success"
        }), 200)

@app.route('/dashboard/data', methods = ['POST'])
def appData():
    clientIds = request.json["clientId"]
    applicationId = request.json["applicationId"]

    data = []

    for clientId in clientIds:
        data.extend(store["clients"].find_one({"_id": ObjectId(clientId)})["clientData"][applicationId])

    data.sort(reverse=True, key = lambda d:d["timestamp"])

    return make_response(jsonify({
            "data": data,
            "status": "Success"
        }), 200)

@app.route('/dashboard/headers', methods = ['POST'])
def appHeaders():
    appId = request.json["applicationId"]

    dataParameters = store["applications"].find_one({"_id": ObjectId(appId)})["dataParameters"]

    return make_response(jsonify({
            "dataParameters": dataParameters,
            "status": "Success"
        }), 200)

@app.route('/dashboard/metrics', methods = ['POST'])
def clientMetrics():
    appId = request.json["applicationId"]
    clientId = request.json["clientId"]

    metrics = store["clients"].find_one({"_id": ObjectId(clientId)})["clientMetrics"][appId]

    print(metrics)

    return make_response(jsonify({
            "metrics": metrics,
            "status": "Success"
        }), 200)

@app.route('/client/metrics', methods = ['POST'])
def pushMetrics():
    appId = request.json["applicationId"]
    clientId = request.json["clientId"]

    store["clients"].update_one({ "_id": ObjectId(clientId)}, { "$set": { "clientMetrics."+appId: request.json["metrics"] } } )

    return make_response(jsonify({
            "status": "Success"
        }), 200)


@app.route('/client/data', methods = ['POST'])
def pushData():
    appId = request.json["applicationId"]
    clientId = request.json["clientId"]

    store["clients"].update_one({ "_id": ObjectId(clientId)}, {"$push": { "clientData."+appId :{ "timestamp": round(time.time() * 1000), "data": request.json["data"] } } } )

    return make_response(jsonify({
            "status": "Success"
        }), 200)


if __name__ == '__main__':
    app.run(port=8080)