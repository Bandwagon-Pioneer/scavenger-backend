from bson.objectid import ObjectId
import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import flask_cors
from datetime import datetime
import random
import newDB

# completely independent of db and api. different service running and being called

with open("CAHpromptsUnvetted.txt", "r") as CAHprompts:
    prompts = []
    for line in CAHprompts.readlines():
        prompts.append(line)

# print(random.choice(prompts))

app = flask.Flask(__name__)
app.config["DEBUG"] = True
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
queue = []


# make backup of queue in database
def make_match():
    global queue
    global prompts
    """
    given a,b,c,d,e,f,...

    take "a" and try match with everyone down the line until either "a" match is made and their both off of the queue, 
    or "a" has no friends and goes to the back of the queue

    maybe have shutoff switch after one full cycle if no new ppl

    ->worry about edge case of no one being compatible


    if odd number of people have reid say on front end that that's the case and the user should get some more friends on board
    """
    """
    does one cycle of the above defined algorithm
    """
    init_user = queue[0]
    prompt = random.choice(prompts)
    print(prompt)
    for user in queue[1:]:
        # change to if queue[0][0] not in user[1][:-1]: if you want to only look at very recent history
        if queue[0][0] not in user[1]:

            # if first person uuid not in history of user
            newDB.db["users"].update_one(
                {"_id": queue[0][0]}, {"$set": {"current_partner": user[0]}}
            )
            newDB.db["users"].update_one(
                {"_id": queue[0][0]}, {"$push": {"partner_history": user[0]}}
            )  # set current partner as user2 for user1 and add user2 to partner history

            newDB.db["users"].update_one(
                {"_id": queue[0][0]}, {"$set": {"current_prompt": prompt}}
            )

            newDB.db["users"].update_one(
                {"_id": user[0]}, {"$set": {"current_partner": queue[0][0]}}
            )  # set current partner as user1 for user2 and add user1 to partner history

            newDB.db["users"].update_one(
                {"_id": user[0]}, {"$push": {"partner_history": queue[0][0]}}
            )

            newDB.db["users"].update_one(
                {"_id": user[0]}, {"$set": {"current_prompt": prompt}}
            )
            queue.remove(queue[0])
            queue.remove(user)
            break
    if init_user in queue:
        queue = queue[1:].append(queue[0])


@app.route("/api/close-match/uuid=<uuid>")
def close_match(uuid):
    # test here, move to newAPI.py
    # $set current_partner: None
    pass


@app.route("/api/join-matchmaking/uuid=<uuid>")
def join_match_making(uuid):
    partner_history = newDB.db["users"].find_one(ObjectId(uuid))["partner_history"]
    # (uuid, partner_history)
    if (ObjectId(uuid), partner_history) not in queue:
        queue.append((ObjectId(uuid), partner_history))
        return {"status": "success"}
    return {"status": "failure"}


@app.route("/api/cancel-match/uuid=<uuid>/passhash=<passhash>")
def cancel_match(uuid, passhash):
    # remove from partner history
    if newDB.req_auth(uuid, passhash):
        user = newDB.db["users"].find_one({"_id": ObjectId(uuid)})
        prev_partner = user["current_partner"]
        newDB.db.users.update_one(
            {"_id": ObjectId(uuid)}, {"$set": {"current_partner": None}}
        )
        newDB.db.users.update_one(
            {"_id": ObjectId(uuid)}, {"$set": {"current_prompt": None}}
        )
        newDB.db.users.update_one(
            {"_id": ObjectId(uuid)}, {"$pop": {"partner_history": 1}}
        )
        newDB.db.users.update_one(
            {"_id": ObjectId(prev_partner)}, {"$set": {"current_partner": None}}
        )
        newDB.db.users.update_one(
            {"_id": ObjectId(prev_partner)}, {"$set": {"current_prompt": None}}
        )
        newDB.db.users.update_one(
            {"_id": ObjectId(prev_partner)}, {"$pop": {"partner_history": 1}}
        )


@app.route("/api/current-match-info/uuid=<uuid>")
def current_match_info(uuid):
    """

    make matches in here

    will give current info on match
    """
    print("making match")
    try:
        make_match()
    except:
        pass
    user = newDB.db.users.find_one({"_id": ObjectId(uuid)})
    return {
        "status": "success",
        "current_partner": str(user["current_partner"]),
        "current_prompt": str(user["current_prompt"]),
    }


@app.errorhandler(Exception)
def error_handled(e):
    return {"status": "failed"}


if __name__ == "__main__":
    app.run()
