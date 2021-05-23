import pandas as pd
import db

candy_budget = 200

lb = db.get_leaderboard()

for person in lb:
    person["candies"] = 0

for i in range(1, 100):
    try:
        for n in range(0, (len(lb) // i)):
            if candy_budget == 0:
                break
            else:
                lb[n]["candies"] += 1
                candy_budget -= 1
    except Exception as e:
        print(e)
        break

sheet = pd.DataFrame(lb)
print(sheet)
print("candy remaining", candy_budget)
sheet.to_csv("candy")
