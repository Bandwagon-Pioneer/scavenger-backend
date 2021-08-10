import pandas

import newDB

# sheet = pandas.DataFrame(data={"email": [], "name": [], "password": []})
emails = []
names = []
passwords = []
users = list(newDB.db.users.find({}))
for user in users:
    # ata = {"email": [], "name": [], "password": []}
    emails.append(user["email"])
    names.append(user["name"])
    passwords.append(user["password"])

sheet = pandas.DataFrame(data={"email": emails, "name": names, "password": passwords})
sheet.to_csv("info.csv")
