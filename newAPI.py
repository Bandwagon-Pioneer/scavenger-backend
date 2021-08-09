import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import flask_cors
from datetime import datetime
import newDB
import random


app = flask.Flask(__name__)
app.config["DEBUG"] = True
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/api/login/email=<email>/passhash=<passhash>")
def login(email, passhash):
    return newDB.login(email, passhash)


@app.route("/api/close-match")
def close_match():
    # will check for parter's submission, if partner submission == None, will wait,
    # elif partner submission != own submission: remove both submissions and say try again
    # elif partner submission == own submission: post submission, give points, and give next partners
    pass


@app.route("/api/submission-feed")
def submission_feed():
    return {"status": "success", "submission_feed": newDB.get_submission_feed()}


@app.route("/api/like-submission")
def like_submission():
    pass


# get_leaderboard -> [{"name1", score}, {"name2", score}]
@app.route("/api/leaderboard")
def leaderboard():
    return {"leaderboard": newDB.get_leaderboard()}


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


# clues for current-location (uuid) -> (clue1, clue2), hat_links
@app.route("/api/current-clues/uuid=<uuid>, passhash=<passhash>")
def current_clues(uuid, passhash):
    return newDB.current_clues(uuid)


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
@app.route("/api/hats/uuid=<uuid>,passhash=<passhash>")
def hats(uuid, passhash):
    # is passhash necessary for this function???
    return newDB.get_hats(uuid)


# rank-and-farthest: returns {"_id": id, "rank": rank, "farthest":nodes_reached}
@app.route("/api/rank/uuid=<uuid>")
def rank(uuid):
    return newDB.get_rank(uuid)


# house points count
@app.route("/api/house-points")
def house_points():
    pass


# sends helpline (Angie's phone number) and the end time of the game
@app.route("/api/game-info")
def game_info():
    return newDB.get_game_info()


@app.errorhandler(Exception)
def error_handled(e):
    return {"status": "failed"}


if __name__ == "__main__":
    app.run(host="192.168.0.14")
