from re import sub
import pymongo
from pymongo import MongoClient
import random
from bson.objectid import ObjectId
from datetime import date, datetime, timedelta
from haversine import haversine, Unit
import pytz
import requests
import time

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

import pickle
from pprint import pprint


def fetch_password(i):
    random.seed(i)
    return random.randint(10000, 99999)


def check_password(db, passhash, uuid):
    # passhash is just the password for now
    user = db["users"].find_one({"_id": ObjectId(uuid)})
    p2check = user["password"]
    if p2check == passhash:
        return True
    else:
        return False


import hashlib


def add_user(db, email, name, i):
    db["users"].insert_one(
        {
            "email": email,
            "name": name,
            "is_moderator": False,
            "password": str(fetch_password(i)),
            "passhash": hashlib.sha256(
                str(fetch_password(i)).encode("ascii")
            ).hexdigest(),
            "active_user": False,  # change to true on first sign in
            "current_partner": None,  # uuid of partner
            "score": 0,
            "hats": [],
            "partner_history": [],  # uuid's of previous partners
            "submission_history": [],  # id's of submission cards
            "current_prompt": None,
            "current_answer": None,
        }
    )


def moderator_remove_submission(mod_uuid, sub_id):
    # check if mod_uuid is actually a mod
    user = db.users.find_one({"_id": ObjectId(mod_uuid)})
    if user["is_moderator"] == True:
        db.submissions.update_one(
            {"_id": ObjectId(sub_id)}, {"$set": {"is_inappropriate": True}}
        )


def add_submission(db, uuid1, uuid2, submission, prompt):
    db["submissions"].insert_one(
        {
            "uuid1": ObjectId(uuid1),
            "uuid2": ObjectId(uuid2),
            "prompt": prompt,
            "submission": submission,
            "is_inappropriate": False,
            "time_submitted": time.time(),
            "num_o_likes": 0,  # = len(likes)
            "num_o_dislikes": 0,  # = len(dislikes)
            "likes": [],  # uuids
            "dislikes": [],  # uuids
        }
    )


def score(uuid):
    user = db.users.find_one({"_id": ObjectId(uuid)})
    s = len(user["submission_history"])
    db.users.update_one({"_id": ObjectId(uuid)}, {"$set": {"score": s}})
    return s


from math import log10


def get_submission_feed():
    submissions = db["submissions"].find({})
    submissions = list(submissions)
    submissions = sorted(
        submissions,
        key=lambda elem: (0.1 * log10(time.time() - elem["time_submitted"]) + 0.001)
        / (0.01 + elem["num_o_likes"] + elem["num_o_dislikes"]),
    )
    results = []
    for sub in submissions:
        if sub["is_inappropriate"] != True:
            sub["_id"] = str(sub["_id"])
            sub["uuid1"] = str(sub["uuid1"])
            sub["uuid2"] = str(sub["uuid2"])
            likes = []
            for l in sub["likes"]:
                likes.append(str(l))
            sub["likes"] = likes
            dislikes = []
            for d in sub["dislikes"]:
                dislikes.append(str(d))
            sub["dislikes"] = dislikes
            results.append(sub)
    return results


# finish likes/dislikes by checking if user has already liked/disliked or not, and if in either don't allow
def like_submission(db, uuid, u_sub_id):
    dislikes_list = db["submissions"].find_one({"_id": ObjectId(u_sub_id)})["dislikes"]
    likes_list = db["submissions"].find_one({"_id": ObjectId(u_sub_id)})["likes"]
    if ObjectId(uuid) not in likes_list and ObjectId(uuid) not in dislikes_list:
        db["submissions"].update_one(
            {"_id": ObjectId(u_sub_id)}, {"$push": {"likes": ObjectId(uuid)}}
        )
        db["submissions"].update_one(
            {"_id": ObjectId(u_sub_id)}, {"$inc": {"num_o_likes": 1}}
        )


def dislike_submission(db, uuid, u_sub_id):
    dislikes_list = db["submissions"].find_one({"_id": ObjectId(u_sub_id)})["dislikes"]
    likes_list = db["submissions"].find_one({"_id": ObjectId(u_sub_id)})["likes"]
    if ObjectId(uuid) not in dislikes_list and ObjectId(uuid) not in likes_list:
        db["submissions"].update_one(
            {"_id": ObjectId(u_sub_id)}, {"$push": {"dislikes": ObjectId(uuid)}}
        )
        db["submissions"].update_one(
            {"_id": ObjectId(u_sub_id)}, {"$inc": {"num_o_dislikes": 1}}
        )


# add unlike and un-dislike
def unlike_submission(db, uuid, u_sub_id):
    if (
        ObjectId(uuid)
        in db["submissions"].find_one({"_id": ObjectId(u_sub_id)})["likes"]
    ):
        db["submissions"].update_one(
            {"_id": ObjectId(u_sub_id)}, {"$pull": {"likes": ObjectId(uuid)}}
        )
        db["submissions"].update_one(
            {"_id": ObjectId(u_sub_id)}, {"$inc": {"num_o_likes": -1}}
        )


def un_dislike_submission(db, uuid, u_sub_id):
    if (
        ObjectId(uuid)
        in db["submissions"].find_one({"_id": ObjectId(u_sub_id)})["dislikes"]
    ):
        db["submissions"].update_one(
            {"_id": ObjectId(u_sub_id)}, {"$pull": {"dislikes": ObjectId(uuid)}}
        )
        db["submissions"].update_one(
            {"_id": ObjectId(u_sub_id)}, {"$inc": {"num_o_dislikes": -1}}
        )


def get_hats(uuid):
    user = db.users.find_one({"_id": ObjectId(uuid)})
    return {"status": "success", "hats": user["hats"]}


def login(email, passhash):
    user = db.users.find_one({"email": email})
    pprint(user)
    if user == None:
        return {"status": "failed"}
    uuid = str(user["_id"])
    if user["passhash"] != passhash:
        return {"status": "failed"}
    if user["active_user"] == False:
        db["users"].update_one({"email": email}, {"$set": {"active_user": True}})
    return {"status": "success", "uuid": uuid, "is_moderator": user["is_moderator"]}


def req_auth(uuid, passhash):
    user = db.users.find_one({"_id": ObjectId(uuid)})
    pprint(user)
    if user == None:
        return False
    if user["passhash"] != passhash:
        return False
    return True


def add_hat(uuid):
    user = db["users"].find_one({"_id": ObjectId(uuid)})
    cur_hats = user["hats"]
    random.shuffle(hat_urls)
    for hat in hat_urls:
        if hat not in cur_hats:
            db.users.update({"_id": ObjectId(uuid)}, {"$push": {"hats": hat}})
            return hat
            break


def get_match(uuid):
    user = db["users"].find_one({"_id": ObjectId(uuid)})
    partner = db["users"].find_one({"_id": ObjectId(user["current_partner"])})


def get_leaderboard():
    active_users = list(db.users.find({"active_user": True}))
    leaderboard = sorted(active_users, key=lambda user: 1 / (user["score"] + 0.01))
    result = []
    for l in leaderboard:
        r = {}
        r["name"] = l["name"]
        r["score"] = l["score"]
        result.append(r)
    return result


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
