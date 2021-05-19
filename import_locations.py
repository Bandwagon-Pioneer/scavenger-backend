import pandas as pd
from db import db, add_node

sheet = pd.read_csv("locations.csv")
print(sheet)
for index, row in sheet.iterrows():
    coords = row["Coords"].split(",")
    add_node(
        db,
        index,
        float(coords[0]),
        float(coords[1]),
        row["Clue/Riddle 1"],
        str(row["Code"].replace('"', "")),
    )
