import pymongo
from pymongo import MongoClient
import random

client = MongoClient()

db_hunt = client.hunt

for i in range(1, 21):
    code = ""
    for j in range(0, 3):
        code += str(random.randint(0,9))
    db_hunt["locations"].insert_one({
        "id": i,
        "text": f"Find Location #{i}",
        "code": code
    })
