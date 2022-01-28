from flask import (
    Blueprint,
    make_response,
    request,
    jsonify)

from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

from watchman.blueprints.database.mongodb import store

load_dotenv()

dashboardRoutes = Blueprint('dashboard', __name__)

@dashboardRoutes.before_request
def keyCheck():
    if(request.json == None or  request.json["apiKey"] != os.getenv("API_KEY")):
        return make_response(jsonify({
            "status": "API Key Missing"
        }), 401)

@dashboardRoutes.route('/dashboard/applications', methods = ['GET'])
def listApplications():

    applications = []

    for app in store["applications"].find():
        applications.append({"applicationName": app["applicationName"], "applicationId": str(app["_id"])})

    return make_response(jsonify({
            "applications": applications,
            "status": "Success"
        }), 200)

@dashboardRoutes.route('/dashboard/clients', methods = ['POST'])
def listClients():
    applicationId = request.json["applicationId"]
    clients = []

    for appClientId in store["applications"].find_one({ "_id": ObjectId(applicationId)})["clients"]:
        client = store["clients"].find_one({ "_id": ObjectId(appClientId)})
        if(client!=None):
            clients.append({"clientName": client["clientName"], "clientId": str(client["_id"])})

    return make_response(jsonify({
            "clients": clients,
            "status": "Success"
        }), 200)

@dashboardRoutes.route('/dashboard/data', methods = ['POST'])
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

@dashboardRoutes.route('/dashboard/headers', methods = ['POST'])
def appHeaders():
    appId = request.json["applicationId"]

    dataParameters = store["applications"].find_one({"_id": ObjectId(appId)})["dataParameters"]

    return make_response(jsonify({
            "dataParameters": dataParameters,
            "status": "Success"
        }), 200)

@dashboardRoutes.route('/dashboard/metrics', methods = ['POST'])
def clientMetrics():
    appId = request.json["applicationId"]
    clientId = request.json["clientId"]

    metrics = store["clients"].find_one({"_id": ObjectId(clientId)})["clientMetrics"][appId]

    return make_response(jsonify({
            "metrics": metrics,
            "status": "Success"
        }), 200)
