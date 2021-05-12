import flask
from flask import request, jsonify
from flask_cors import CORS,cross_origin
import flask_cors
from datetime import datetime
import db
import random

app = flask.Flask(__name__)
app.config["DEBUG"] = True
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

def sort_scores(userscore):
    return userscore['score']

@app.route("/api/current-location", methods=['GET', 'POST'])
@cross_origin()
def cur_location():
    print('getting current location')
    user = db.get_user("foo")
    loc = db.get_location(user["location"])
    return loc

@app.route("/api/next-location", methods=['POST'])
@cross_origin()
def next_location():
    """
    app sends
    {
        uuid: 018932,   # some unique identifier for the user
        code: 528,       # the code to verify
    }
    """
    req_data = flask.request.json
    code = req_data['code']
    uuid = req_data['uuid']
    print(f'got code {code} for user {uuid}')
    data = db.check_code(code)
    if(data["status"] == "success"):
        return data

@app.route("/api/user-data", methods=['GET', 'POST'])
@cross_origin()
def user_data():
    scores = []
    for i in range(0, 30):
        scores.append({'name': 'other', 'score': random.randint(0, 20)})

    scores.sort(key=sort_scores,reverse=True)
    scores[random.randint(0, 29)]['name'] = 'user'
    print(scores)
    return(jsonify({"scores": scores}))


app.run(host='192.168.0.14')
    