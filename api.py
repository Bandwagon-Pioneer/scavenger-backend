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


# get_leaderboard -> [{"name1", nodes_so_far}, {"name2", nodes_so_far}]
@app.route("/api/leaderboard")
def leaderboard():
    return {"leaderboard": db.get_leaderboard()}


# submit_code -> updates_user_path && returns (clue1, clue2) for next node
# if current index = 7 return you are done!!!!!
# send code to server as string
@app.route("/api/submit/uuid=<uuid>/code=<code>")
def submit_code(uuid, code):
    return db.handle_code(uuid, code)


# login (email) -> ObjectId #remember to index on email, as well to make login fast!
@app.route("/api/login/<email>")
def login(email):
    return {"uuid": db.login(email)}


# clues for current-location (uuid) -> (clue1, clue2), hat_links
@app.route("/api/current-clues/<uuid>")
def current_clues(uuid):
    return db.current_clues(uuid)


# hat_links
@app.route("/api/hats/<uuid>")
def hats(uuid):
    return db.get_hats(uuid)


app.run()
