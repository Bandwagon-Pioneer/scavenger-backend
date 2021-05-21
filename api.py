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


# submit: if on 14th or less node then returns
"""
{
  "clues": {
    "clue1": "You know this one, you've been here before. Music and memories behind this purple door", 
    "clue2": "https://cdn.discordapp.com/attachments/844619356779839508/844621949543907348/image0.jpg"
  }, 
  "newhat": "https://cdn.discordapp.com/attachments/820148747882332180/844039652712906782/image9.png", 
  "status": "success"
}
"""
# if on 15th node then returns
# {"status" : "completed"}
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


# hat_links: returns
"""
{
  "hats": [
    "https://cdn.discordapp.com/attachments/820148747882332180/844039651286056960/image6.png", 
    "https://cdn.discordapp.com/attachments/820148747882332180/844039649331904512/image0.png", 
    "https://cdn.discordapp.com/attachments/820148747882332180/844039682882535424/image4.png",
    ],
  "status":"success"

"""
#
@app.route("/api/hats/uuid=<uuid>")
def hats(uuid):
    return db.get_hats(uuid)


# rank-and-farthest: returns {"_id": id, "rank": rank, "farthest":nodes_reached}
@app.route("/api/rank-and-farthest/uuid=<uuid>")
def rank(uuid):
    return db.get_rank_and_farthest(uuid)


app.run()
