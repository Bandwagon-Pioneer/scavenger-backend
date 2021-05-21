import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import flask_cors
from datetime import datetime
import db
import random


app = flask.Flask(__name__)
app.config["DEBUG"] = True
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


# get_leaderboard -> [{"name1", nodes_so_far, score}, {"name2", nodes_so_far,score}]
@app.route("/api/leaderboard")
def leaderboard():
    return {"leaderboard": db.get_leaderboard()}


"""
{
  "clues": {
    "clue1": "Find four small diamonds with a fence all around. Behind the tennis courts is where I'll be found,."
  }, 
  "newhat": "https://cdn.discordapp.com/attachments/820148747882332180/844039682651455539/image3.png", 
  "status": "success"
}

"""


@app.route("/api/submit/uuid=<uuid>/code=<code>")
def submit_code(uuid, code):
    return db.handle_code(uuid, code)


# login (email) -> ObjectId #remember to index on email, as well to make login fast!
@app.route("/api/login/email=<email>")
def login(email):
    return {"uuid": db.login(email)}


# clues for current-location (uuid) -> (clue1, clue2), hat_links
@app.route("/api/current-clues/uuid=<uuid>")
def current_clues(uuid):
    return db.current_clues(uuid)


# hat_links
@app.route("/api/hats/uuid=<uuid>")
def hats(uuid):
    return db.get_hats(uuid)


# returns {"_id": id, "rank": rank}
@app.route("/api/rank-and-farthest/uuid=<uuid>")
def rank(uuid):
    return db.get_rank_and_farthest(uuid)


app.run()
