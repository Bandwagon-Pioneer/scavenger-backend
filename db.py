import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import random
import re
client = MongoClient()

db_hunt = client.hunt
locations = db_hunt["locations"]
users = db_hunt["users"]

def get_location(id):
    try:
        location = locations.find_one({"id": id})
        return({"text": location["text"], "status": "success"})    
    except Exception as e:
        print(e)
        return ({"status":"failed"})

def get_user_location(uuid):
    try:
        print(uuid)
        oid = ObjectId(uuid)
        print(oid)
        user = users.find_one({"_id": oid})
        print(f"found user {user}")
        location = locations.find_one({"id": user['location']})
        print(f"found location {location}")
        return({"status": "success", "text": location["text"]})
    except Exception as e:
        print(e)
        return({"status": "failed"})

def get_random_location():
    try:
        location = locations.find_one({"id": random.randint(1,locations.count())})
        return location
    except Exception as e:
        print(e)
        return ({"status":"failed"})

def check_code(code, uuid):
    print(f'checking code {code}')
    try:
        user = users.find_one({"_id": ObjectId(uuid)})
        if(user != None):
            if(locations.find_one({"id": user["location"]})["code"] == code):
                print(f"code {code} is correct, selecting new location")
                new_loc = user["location"]
                while new_loc == user["location"]:
                    new_loc = random.randint(1,locations.count())
                set_location(uuid, new_loc)
                return(get_location(user["location"]))
            else:
                print(f"code {code} is incorrect")
                return({"status": "incorrect code"})
        else:
            return({"status": "invalid user"})
    except Exception as e:
        print(e)
        return({"status": "failed"})

def log_in(email):
    try:
        user = users.find_one({"email": email})
        if(user != None):
            return {"status": "success", "uuid": str(user["_id"])}
        else:
            users.insert_one({"email": email, "location": 1})
            user = users.find_one({"email": email})
            uuid = {"id": str(user["_id"])}
            return {"status": "success", "uuid": uuid}
    except Exception as e:
        print(e)
        return({"status": "failed"})


def get_user(uuid):
    try:
        user = users.find_one({"_id": ObjectId(uuid)})
        return({"status": "success", "user": user})
    except Exception as e:
        print(e)
        return({"status": "failed"})

def set_location(uuid, lid):
    try:
        users.update_one({"_id": ObjectId(uuid)},{"$set":{"location":lid}})
        return({"status": "success"})
    except Exception as e:
        print(e)
        return({"status": "failed"})