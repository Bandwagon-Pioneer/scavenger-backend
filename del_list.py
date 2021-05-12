import pymongo
from pymongo import MongoClient
import datetime
import random

client = MongoClient()

db_hunt = client.hunt

for i in range(1, 21):
    db_hunt["locations"].delete_one({"id":i})
