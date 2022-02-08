import pymongo
import os
from dotenv import load_dotenv
import time

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
store = pymongo.MongoClient(MONGO_URI)["watchman"]

for client in store["clients"].find({}):
    clientMetrics = client["clientMetrics"]
    metricArchive = client["metricArchive"]

    applicationMetricAvailableIds = metricArchive.keys()
    applicationIds = clientMetrics.keys()

    for applicationId in applicationIds:
        metrics = clientMetrics[applicationId]

        metrics["timestamp"] = round(time.time() * 1000)

        store["clients"].update_one({"_id": client["_id"]},{"$push": { "metricArchive."+applicationId : metrics } } )

        


