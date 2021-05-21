from db import add_node, add_user
import db
import random
import json

db.db.users.delete_many({})

with open("ordered_ppl.txt") as ppl:
    data = json.load(ppl)
    for person in data["people"]:
        add_user(
            db.db,
            person["email"],
            person["name"],
            None,
        )
