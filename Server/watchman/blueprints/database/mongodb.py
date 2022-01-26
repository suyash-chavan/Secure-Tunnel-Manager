import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

store = pymongo.MongoClient(MONGO_URI)["watchman"]