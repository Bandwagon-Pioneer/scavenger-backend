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
    if len(queue) > 1:
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


@app.route("/api/close-match/uuid=<uuid>/passhash=<passhash>", methods=["POST"])
def close_match(uuid, passhash):
    # test here, move to newAPI.py
    # $set current_partner: None
    """
    data = {
        "submission": "bablbalsbfusgv absdiabgv basfbia funny business kajbsfiabg abaiusdfb."
    }
    """
    data = request.json
    if newDB.req_auth(uuid, passhash):
        submission = data["submission"]
        # newDB["submissions"].insert_one
        newDB.db["users"].update_one(
            {"_id": ObjectId(uuid)},
            {"$set": {"current_answer": submission}},
        )
        user = newDB.db["users"].find_one({"_id": ObjectId(uuid)})
        partner = newDB.db["users"].find_one({"_id": user["current_partner"]})
        if partner["current_answer"] == None:
            return {"status": "success", "message": "waiting on partner"}
        elif partner["current_answer"].lower() == submission.lower():
            newDB.add_submission(
                db=newDB.db,
                uuid1=ObjectId(uuid),
                uuid2=user["current_partner"],  # uuid
                submission=submission,
                prompt=user["current_prompt"],
            )
            # add points to both users??
            # then set current partner to None
            # and add the submission to his history
            newDB.db["users"].update_one(
                {"_id": ObjectId(uuid)},
                {
                    "$push": {
                        "submission_history": {
                            "prompt": user["current_prompt"],
                            "submission": submission,
                            "user1": ObjectId(uuid),
                            "user2": user["current_partner"],
                        }
                    }
                },
            )
            newDB.db["users"].update_one(
                {"_id": user["current_partner"]},
                {
                    "$push": {
                        "submission_history": {
                            "prompt": user["current_prompt"],
                            "submission": submission,
                            "user1": ObjectId(uuid),
                            "user2": user["current_partner"],
                        }
                    }
                },
            )
            newDB.db["users"].update_one(
                {"_id": ObjectId(uuid)}, {"$set": {"current_prompt": None}}
            )
            newDB.db["users"].update_one(
                {"_id": user["current_partner"]}, {"$set": {"current_prompt": None}}
            )
            newDB.db["users"].update_one(
                {"_id": ObjectId(uuid)}, {"$set": {"current_answer": None}}
            )
            newDB.db["users"].update_one(
                {"_id": user["current_partner"]}, {"$set": {"current_answer": None}}
            )
            newDB.db["users"].update_one(
                {"_id": user["current_partner"]}, {"$set": {"current_partner": None}}
            )
            newDB.db["users"].update_one(
                {"_id": ObjectId(uuid)}, {"$set": {"current_partner": None}}
            )
            return {"status": "success", "message": "answers are equivalent"}
        elif partner["current_answer"].lower() != submission.lower():
            # set both current_answers to None, and return {"status":"success","message": "mismatched answers, put in the same answer as partner"}
            newDB.db["users"].update_one(
                {"_id": ObjectId(uuid)}, {"$set": {"current_answer": None}}
            )
            newDB.db["users"].update_one(
                {"_id": partner["_id"]}, {"$set": {"current_answer": None}}
            )
            return {
                "status": "success",
                "message": "mismatched answers, put in the same answer as partner",
            }
        else:
            return {
                "status": "failed",
                "message": "authenticated fine, but something went wrong after that",
            }
    return {"status": "failed", "message": "you at least are still on the endpoint"}


@app.route("/api/join-matchmaking/uuid=<uuid>/passhash=<passhash>")
def join_match_making(uuid, passhash):
    global queue
    print(queue)
    if newDB.req_auth(uuid, passhash):
        print("join match auth success")
        partner_history = newDB.db["users"].find_one(ObjectId(uuid))["partner_history"]
        # (uuid, partner_history)
        if (ObjectId(uuid), partner_history) not in queue:
            print("not in queue")
            queue.append((ObjectId(uuid), partner_history))
            return {"status": "success"}
    return {"status": "failure"}


def clear_all_partner_hists():
    newDB.db.users.update_many({}, {"$pop": {"partner_history": 1}})
    newDB.db.users.update_many({}, {"$set": {"current_partner": None}})
    newDB.db.users.update_many({}, {"$set": {"current_prompt": None}})


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
        return {"status": "success"}
    return {"status": "failed"}


@app.route("/api/current-match-info/uuid=<uuid>")
def current_match_info(uuid):
    global queue
    print("queue = ", queue)
    """
    make matches in here

    will give current info on match
    """
    print("making match")
    try:
        make_match()
    except Exception as e:
        print(e)
    user = newDB.db.users.find_one({"_id": ObjectId(uuid)})
    return {
        "status": "success",
        "matched": True if user["current_partner"] != None else False,
        "current_partner": str(user["current_partner"]),
        "current_prompt": str(user["current_prompt"]),
    }


"""
UNCOMMENT ME!!!!!!!

@app.errorhandler(Exception)
def error_handled(e):
    return {"status": "failed"}
"""

if __name__ == "__main__":
    app.run(port=80)
