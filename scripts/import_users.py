import json
from pprint import pprint

json_ppl = {}

json_ppl["people"] = []

with open("band_people.txt") as jfile:
    data = json.load(jfile)
    for thing in data["people"][0][0][2]:
        person = {"name": thing[1], "email": thing[2]}
        if person not in json_ppl["people"]:
            json_ppl["people"].append(person)


with open("band_people_last_year.txt") as jfile:
    data = json.load(jfile)
    for thing in data["people"][0][0][2]:
        person = {"name": thing[1], "email": thing[2]}
        if person not in json_ppl["people"]:
            json_ppl["people"].append(person)

with open("ordered_ppl.txt", "w") as outfile:
    json.dump(json_ppl, outfile)
