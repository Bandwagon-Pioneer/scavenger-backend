from flask import Flask
from flask import request
import random

app = Flask(__name__)


@app.route("/")
def index():
    return {"status": "Great success!"}


token_db = [  # just ask if token in token_db: do_stuff()
    "asdaasdasdasda",
    "asdfudbfrgvb",
    "adfrigb4ovwd",
    "bfefbjendfon",
    "iuwhrg",
    "2768gyufjrn",
]
node_codes_db = {"i6": "i6code", "J8": "J8code", "f9": "f9code", "7S": "7Scode"}


class User:
    def __init__(self, token):
        self.token = token
        self.nodes = random.shuffle([node for node in node_codes_db.keys()])
        self.current_index = 0

    def check_code(self, code):
        if code == self.nodes[self.current_index]:
            return True
        else:
            return False

    def next_node(self, code):
        try:
            if self.check_code(code) == False:
                return None
            else:
                self.current_index += 1
                return self.nodes[self.current_index]
        except:
            return None


users = [User(token) for token in token_db]

# http://10.1.1.1:5000/api/submit-code?uuid=018932&code=J8
@app.route("/api/submit-code")
def submit_code():
    uuid = request.args.get("uuid")
    code = request.args.get("code")
    for user in users:
        if user.token == uuid:
            u = user
            break
        else:
            u = None
    if u == None:
        return {"status": 404}
    elif code != u:
        return {"status": 404}
    return {"next_clue": None}


app.run(debug=True)
