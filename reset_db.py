from newDB import add_user
import newDB
import random
import json

newDB.db.users.delete_many({})

with open("ordered_ppl.txt") as ppl:
    data = json.load(ppl)
    i = 0
    for person in data["people"]:
        add_user(newDB.db, person["email"], person["name"], i=i)
        i += 1
