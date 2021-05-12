import pymongo
from pymongo import MongoClient
import datetime
import random

client = MongoClient()

db_hunt = client.hunt

def get_location(id):
    locations = db_hunt["locations"]
    try:
        location = locations.find_one({"id": id})
        return({"text": location["text"], "status": "success"})    
    except Exception as e:
        print(e)
        return ({"status":"failed"})

def get_random_location():
    locations = db_hunt["locations"]
    try:
        location = locations.find_one({"id": random.randint(1,locations.count())})
        return location;
    except Exception as e:
        print(e)
        return ({"status":"failed"})

def check_code(code):
    users = db_hunt["users"]
    locations = db_hunt["locations"]
    print(f'checking code {code}')
    try:
        user = users.find_one({"id": 'foo'})
        if(locations.find_one({"id": user["location"]})["code"] == code):
            print(f"code {code} is correct, selecting new location")
            new_loc = user["location"]
            while new_loc == user["location"]:
                new_loc = random.randint(1,locations.count())
            set_location(new_loc)
            return(get_location(user["location"]))
        else:
            print(f"code {code} is incorrect")
            return({"status": "incorrect"})
    except Exception as e:
        print(e)
        return({"status": "failed"})

def get_user(id):
    users = db_hunt["users"]
    try:
        user = users.find_one({"id": id})
        return user
    except Exception as e:
        print(e)
        return({"status": "failed"})

def set_location(id):
    users = db_hunt["users"]
    try:
        users.update_one({"id":"foo"},{"$set":{"location":id}})
        return({"status": "success"})
    except Exception as e:
        print(e)
        return({"status": "failed"})