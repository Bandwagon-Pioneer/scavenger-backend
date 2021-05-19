from db import add_node, add_user
import db
import random
import json

hat_urls = [
    "https://cdn.discordapp.com/attachments/820148747882332180/844039682882535424/image4.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039682651455539/image3.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039682244739113/image2.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039681955856394/image1.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039681653997578/image0.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039652712906782/image9.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039652327555082/image8.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039651794616330/image7.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039651286056960/image6.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039650909749258/image5.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039650552447016/image4.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039650267496448/image3.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039649932738560/image2.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039649659846696/image1.png",
    "https://cdn.discordapp.com/attachments/820148747882332180/844039649331904512/image0.png",
]


# add fake nodes
"""
for i in range(20):
    add_node(
        db.db,
        i,
        round(random.uniform(500, 800), 3),
        round(random.uniform(500, 800), 3),
        "clue1",
        "clue2",
    )
"""
# add users
with open("ordered_ppl.txt") as ppl:
    data = json.load(ppl)
    for person in data["people"]:
        add_user(
            db.db,
            person["email"],
            person["name"],
            None,
        )
