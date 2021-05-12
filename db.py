import pymongo
from pymongo import MongoClient
import random

client = MongoClient("localhost", 27017)

db = client["scavengerHunt"]


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


# setup
# db.create_collection("nodes")
# db.create_collection("users")
def costruct_node(nodeid, latitude, longitude, clue1, clue2):
    try:
        code = get_node_code(nodeid)
    except:
        raise IndexError

    return {
        "nodeid": nodeid,
        "code": code,  # db.get_node_code(nodeid)
        "latitude": latitude,
        "longitude": longitude,
        "clue1": clue1,  # "img|"+"https://cdn.asdaad.com" OR "txt|"+"some fantastic clue"
        "clue2": clue2,
    }


def add_node(db, nodeid, latitude, longitude, clue1, clue2):
    node = costruct_node(nodeid, latitude, longitude, clue1, clue2)
    db["nodes"].insert_one(node)


def add_user(db, email, name, profile_pic):
    db["nodes"].insert_one({"email": email, "name": name, "profile_pic": profile_pic})


def next_node(uuid):
    pass


def distance(node1_id, node2_id):
    # retrieves longitude and latitude of each node and performs haversine distance
    pass
