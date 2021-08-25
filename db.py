import pymongo
from pymongo import MongoClient
import random
from bson.objectid import ObjectId
from datetime import date, datetime, timedelta
from haversine import haversine, Unit
import pytz
import requests

client = MongoClient("localhost", 27017)

db = client["scavengerHunt"]

hat_urls = [
    "https://cdn.discordapp.com/attachments/820148747882332180/844039682882535424/image4.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039682651455539/image3.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039682244739113/image2.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039681955856394/image1.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039681653997578/image0.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039652712906782/image9.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039652327555082/image8.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039651794616330/image7.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039651286056960/image6.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039650909749258/image5.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039650552447016/image4.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039650267496448/image3.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039649932738560/image2.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039649659846696/image1.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039649331904512/image0.png",
]


# setup/helper functions


def add_node(db, userid, clue1, code):
    """
    users are the 'locations', so userid identifies them
    """
    db["nodes"].insert_one(
        {
            "userid": userid,
            "code": code,  # db.get_node_code(userid)
            "clue1": clue1,
            "clue2": None,  # "img|"+"https://cdn.asdaad.com" OR "txt|"+"some fantastic clue"
        }
    )


def create_path():
    res = db["nodes"].aggregate(
        [
            {"$sample": {"size": 15}},
            {
                "$project": {
                    "_id": 1,
                    "code": 1,
                    "latitude": 1,
                    "longitude": 1,
                    "clue1": 1,
                    "clue2": 1,
                }
            },
        ]
    )
    res = list(res)
    for i in range(0, len(res)):
        res[i]["index"] = i
        res[i]["start"] = None
        res[i]["stop"] = None
    return res


import pickle
from pprint import pprint


def fetch_password(i):
    file_name = "passwords.pkl"
    open_file = open(file_name, "rb")
    loaded_list = pickle.load(open_file)
    pword = loaded_list[i]
    open_file.close()
    return pword


def check_password(db, passhash, uuid):
    # passhash is just the password for now
    user = db["users"].find_one({"_id": ObjectId(uuid)})
    p2check = user["password"]
    if p2check == passhash:
        return True
    else:
        return False


import hashlib


def add_user(db, email, name, profile_pic, i):
    route = create_path()
    db["users"].insert_one(
        {
            "email": email,
            "name": name,
            "password": fetch_password(i),
            "passhash": hashlib.sha256(fetch_password(i).encode("ascii")).hexdigest(),
            "score": 0,
            "hats": [],
        }
    )


def initialize_location(uuid):
    now = datetime.utcnow()
    id = ObjectId(uuid)
    db.users.update_one({"_id": id}, {"$set": {"path.0.start": now}})


def score():
    pass


def update_score(uuid):
    pass
    db.users.update_one({"_id": ObjectId(uuid)}, {"$set": {"score": score()}})


def get_leaderboard():
    pipeline = [
        {"$match": {"current_index": {"$gt": 0}}},
        {"$project": {"name": 1, "current_index": 1, "score": 1, "_id": 0}},
    ]
    return sorted(
        list(db.users.aggregate(pipeline=pipeline)),
        key=lambda k: k["score"],
        reverse=True,
    )


def get_rank(uuid):
    pipeline = [
        {"$match": {"current_index": {"$gt": 0}}},
        {"$project": {"_id": 1, "score": 1, "current_index": 1}},
    ]
    leaders = sorted(
        list(db.users.aggregate(pipeline=pipeline)),
        key=lambda k: k["score"],
        reverse=True,
    )
    rank = None
    for i in range(len(leaders)):
        if uuid == str(leaders[i]["_id"]):
            rank = i + 1
            break
    return {"status": "success", "rank": rank}


def current_clue(uuid):
    user = db.users.find_one({"_id": ObjectId(uuid)})
    current_index = user["current_index"]
    if current_index < 14:
        return {
            "status": "success",
            "clue1": user["path"][current_index]["clue1"],
        }
    else:
        return {"status": "success", "clue1": "You finished! Congrats!"}


def handle_code(uuid, code, passhash):
    user = db.users.find_one(ObjectId(uuid))
    if check_password(db, passhash, uuid):
        current_index = user["current_index"]
        if current_index == 14:
            hat = add_hat(uuid)
            update_score(uuid)
            return {"status": "completed", "newhat": hat}
        elif str(code) == user["path"][current_index]["code"]:
            update_location(uuid)
            update_score(uuid)
            hat = add_hat(uuid)
            return {"status": "success", "clues": current_clues(uuid), "newhat": hat}
        else:
            return {"status": "failed"}
    else:
        return {"status": "failed"}


def login(email, passhash):
    user = db.users.find_one({"email": email})
    pprint(user)
    if user == None:
        return {"status": "failed"}
    uuid = str(user["_id"])
    if user["passhash"] != passhash:
        return {"status": "failed"}
    return {"status": "success", "uuid": uuid}


def add_hat(uuid):
    user = db["users"].find_one({"_id": ObjectId(uuid)})
    cur_hats = user["hats"]
    random.shuffle(hat_urls)
    for hat in hat_urls:
        if hat not in cur_hats:
            db.users.update({"_id": ObjectId(uuid)}, {"$push": {"hats": hat}})
            return hat
            break


def get_hats(uuid):
    user = db.users.find_one({"_id": ObjectId(uuid)})
    return {"status": "success", "hats": user["hats"]}


def get_game_info():
    endtime = db.endtime.find_one({})
    return {
        "status": "success",
        "endtime": "The End of Band Camp",
    }


def make_error():
    raise Exception("big bad error")
