from email.mime import application
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

    print(applications)

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
        try:
            data.extend(store["clients"].find_one({"_id": ObjectId(clientId)})["clientData"][applicationId])
        except Exception as e:
            pass

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

    metricVars = store["applications"].find_one({"_id": ObjectId(appId)})["metricParameters"]

    metricImages = store["applications"].find_one({"_id": ObjectId(appId)})["metricImages"]

    metricReceived = store["clients"].find_one({"_id": ObjectId(clientId)})["clientMetrics"][appId]

    metrics = {}
    images = {}

    for metricHeader in metricVars.keys():
        if metricVars[metricHeader] in metricReceived.keys():
            try:
                metrics[metricHeader] = metricReceived[metricVars[metricHeader]]
            except Exception as e:
                pass

            try:
                images[metricHeader] = metricImages[metricVars[metricHeader]]
            except Exception as e:
                pass
            
    return make_response(jsonify({
            "metrics": metrics,
            "images": images,
            "status": "Success"
        }), 200)

@dashboardRoutes.route('/dashboard/application/register', methods = ['POST'])
def registerApplication():
    reqJson = request.json

    applicationName = reqJson["applicationName"]
    dataParameters = reqJson["dataParameters"]
    metricParameters = reqJson["dataParameters"]

    store["applications"].insert_one({
        "applicationName": applicationName,
        "dataParameters": dataParameters,
        "metricParameters": metricParameters,
        "clients": []
    })
            
    return make_response(jsonify({
            "status": "Success"
        }), 200)

@dashboardRoutes.route('/dashboard/application/info', methods = ['POST'])
def applicationInfo():
    reqJson = request.json

    applicationId = reqJson["applicationId"]

    applicationInfo = store["applications"].find_one({"_id": ObjectId(applicationId)})
    
    applicationInfoRes = {}
    applicationInfoRes["applicationName"] = applicationInfo["applicationName"]
    applicationInfoRes["dataParameters"] = applicationInfo["dataParameters"]
    applicationInfoRes["metricParameters"] = applicationInfo["metricParameters"]
            
    return make_response(jsonify({
            "applicationInfo": applicationInfoRes,
            "status": "Success"
        }), 200)

@dashboardRoutes.route('/dashboard/application/update', methods = ['POST'])
def applicationUpdate():
    reqJson = request.json

    applicationId = reqJson["applicationId"]
    applicationName = reqJson["applicationName"]
    dataParameters = reqJson["dataParameters"]
    metricParameters = reqJson["metricParameters"]

    store["applications"].update_one({"_id": ObjectId(applicationId)},{"$set": {"applicationName": applicationName, "dataParameters": dataParameters, "metricParameters": metricParameters}})
            
    return make_response(jsonify({
            "status": "Success"
        }), 200)
