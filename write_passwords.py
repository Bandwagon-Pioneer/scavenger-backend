import requests
import json
import random

N = 500

count = f"?count={N}"
noun_url = "https://random-word-form.herokuapp.com/random/noun" + count
adjective_url = "https://random-word-form.herokuapp.com/random/adjective" + count
noun_resp = requests.get(noun_url)
adj_resp = requests.get(adjective_url)
# print(noun_resp)
nouns = json.loads(noun_resp.text)
adjs = json.loads(adj_resp.text)

# print(nouns)

with open("generated_passwords.txt", "w") as passwords:
    for i in range(N):
        password = (
            adjs[i].capitalize() + nouns[i].capitalize() + str(random.randint(10, 99))
        )
        passwords.write(password + "\n")
