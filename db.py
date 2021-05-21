import pymongo
from pymongo import MongoClient
import random
from bson.objectid import ObjectId
from datetime import date, datetime, timedelta
from haversine import haversine, Unit
import pytz

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
def get_node_code(n):
    # it doesn't have to be unique
    if n > 999:
        num = int(str(n + random.randint(0, 99))[:2])
    else:
        num = n + random.randint(100, 900)

    stnum = str(num)
    l = len(stnum)
    if l == 1:
        return "00" + stnum
    elif l == 2:
        return "0" + stnum
    elif l == 3:
        return stnum
    elif l == 0:
        raise ValueError
    else:
        return stnum[:2]


def costruct_node(nodeid, latitude, longitude, clue1, clue2, code):

    return {
        "nodeid": nodeid,
        "code": code,  # db.get_node_code(nodeid)
        "latitude": latitude,
        "longitude": longitude,
        "clue1": clue1,
        "clue2": clue2,  # "img|"+"https://cdn.asdaad.com" OR "txt|"+"some fantastic clue"
    }


def add_node(db, nodeid, latitude, longitude, clue1, clue2, code):
    node = costruct_node(nodeid, latitude, longitude, clue1, clue2, code)
    db["nodes"].insert_one(node)


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


def add_user(db, email, name, profile_pic):
    route = create_path()
    db["users"].insert_one(
        {
            "email": email,
            "name": name,
            "profile_pic": profile_pic,
            "average_speed": 0,
            "score": 0,
            "hats": [],
            "current_index": 0,
            "path": route,
        }
    )


def initialize_location(uuid):
    try:
        now = datetime.utcnow()
        id = ObjectId(uuid)
        db.users.update_one({"_id": id}, {"$set": {"path.0.start": now}})
    except Exception as e:
        print(e)
        return {"status": "failed"}


def update_location(uuid):
    try:
        now = datetime.utcnow()
        id = ObjectId(uuid)
        user = db["users"].find_one({"_id": id})
        current_index = user["current_index"]
        if current_index < 14:
            db.users.update_one(
                {"_id": id}, {"$set": {f"path.{current_index}.stop": now}}
            )
            db.users.update_one(
                {"_id": id}, {"$set": {f"path.{current_index+1}.start": now}}
            )
            db.users.update_one(
                {"_id": id}, {"$set": {"current_index": current_index + 1}}
            )
        elif current_index == 14:
            db.users.update_one(
                {"_id": id}, {"$set": {f"path.{current_index}.stop": now}}
            )

    except Exception as e:
        print(e)
        return {"status": "failed"}


def get_velocity(uuid):
    try:
        user = db.users.find_one({"_id": ObjectId(uuid)})
        path = user["path"]
        farthest_index = user["current_index"]
        if farthest_index > 0:
            dt = (path[farthest_index]["start"] - path[0]["start"]).total_seconds()
            dx = 0

            for i in range(0, len(path) - 2):
                a = (path[i]["latitude"], path[i]["longitude"])
                b = (path[i + 1]["latitude"], path[i + 1]["longitude"])
                dist = haversine(a, b, unit="m")
                dx += dist
            return dx / dt
        else:
            return 0
    except Exception as e:
        print(e)
        return {"status": "failed"}


def update_velocity(uuid):
    try:
        velocity = get_velocity(uuid)
        db.users.update_one(
            {"_id": ObjectId(uuid)}, {"$set": {"average_speed": velocity}}
        )
    except Exception as e:
        print(e)
        return {"status": "failed"}


def score(path_index, avg_velocity):
    return (path_index + 1) * avg_velocity


def update_score(uuid):
    try:
        update_velocity(uuid)
        user = db.users.find_one({"_id": ObjectId(uuid)})
        path_index = user["current_index"]
        velocity = user["average_speed"]
        db.users.update_one(
            {"_id": ObjectId(uuid)}, {"$set": {"score": score(path_index, velocity)}}
        )
    except Exception as e:
        print(e)
        return {"status": "failed"}


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


def get_rank_and_farthest(uuid):
    try:
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
        farthest = None
        for i in range(len(leaders)):
            if uuid == str(leaders[i]["_id"]):
                rank = i + 1
                farthest = leaders[i]["current_index"] + 1
                break
        return {"status": "success", "rank": rank, "farthest": farthest}
    except Exception as e:
        print(e)
        return {"status": "failed"}


def get_end_time():
    endtime = db.endtime.find_one({"_id": ObjectId("60a48ef494ea8cb54a243443")})
    return endtime


# business stuff


def current_clues(uuid):
    try:
        user = db.users.find_one({"_id": ObjectId(uuid)})
        current_index = user["current_index"]

        return {
            "clue1": user["path"][current_index]["clue1"],
            "clue2": user["path"][current_index]["clue2"],
        }
    except Exception as e:
        print(e)
        return {"status": "failed"}


def handle_code(uuid, code):
    try:
        user = db.users.find_one(ObjectId(uuid))
        current_index = user["current_index"]
        if current_index == 14:
            return {"status": "completed"}
        elif str(code) == user["path"][current_index]["code"]:
            update_location(uuid)
            update_score(uuid)
            hat = add_hat(uuid)
            return {"status": "success", "clues": current_clues(uuid), "newhat": hat}
        else:
            return {"status": "failed"}
    except Exception as e:
        print(e)
        return {"status": "failed"}


# remember to wrap in try block
def login(email):
    user = db.users.find_one({"email": email})
    uuid = str(user["_id"])
    print(user["path"][0]["start"])
    if user["path"][0]["start"] == None:
        initialize_location(uuid)
    return uuid


def clue2_time(uuid):
    try:
        user = db.users.find_one({"_id": ObjectId(uuid)})
        current_index = user["current_index"]
        start = user["path"][current_index]["start"]
        return {
            "status": "success",
            "clue2time": round((start + timedelta(minutes=3)).timestamp()),
        }
    except Exception as e:
        print(e)
        return {"status": "failed"}


def add_hat(uuid):
    try:
        user = db["users"].find_one({"_id": ObjectId(uuid)})
        cur_hats = user["hats"]
        random.shuffle(hat_urls)
        for hat in hat_urls:
            if hat not in cur_hats:
                db.users.update({"_id": ObjectId(uuid)}, {"$push": {"hats": hat}})
                return hat
                break
    except Exception as e:
        print(e)
        return {"status": "failed"}


def get_hats(uuid):
    try:
        user = db.users.find_one({"_id": ObjectId(uuid)})
        return {"status": "success", "hats": user["hats"]}
    except Exception as e:
        print(e)
        return {"status": "failed"}
