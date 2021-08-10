from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
import re
import time
import random
import newDB

users = 



driver = webdriver.Chrome("/Users/jeremi/Desktop/chromedriver")

driver.get("https://gmail.com")
username = "2022formanduranonajeremij@aaps.k12.mi.us"
password = "salt85MoleLOL"

email = driver.find_element_by_id("identifierId")
email.send_keys(username)
email.send_keys(Keys.RETURN)
time.sleep(2)
pasinp = driver.find_element_by_name("password")
pasinp.send_keys(password)
pasinp.send_keys(Keys.RETURN)
# input("press any button after you've okayed it on the phone")


time.sleep(5)
driver.get("https://mail.google.com/mail/u/0/#inbox?compose=new")
time.sleep(5)
to = driver.find_element_by_name("to")
subject = driver.find_element_by_name("""subjectbox""")
body = driver.find_element_by_xpath("""//*[@id=":97"]""")
time.sleep(2)
to.send_keys("2022formanduranonajeremij@aaps.k12.mi.us")
time.sleep(0.25)
subject.send_keys("Your Password for Bandwagon: Band Camp Super Bonanza")
time.sleep(0.25)
body.send_keys(f"""Hello {to_name}!!!

Though you're probably asleep by now, the night before we head out for band camp, I wanted to let you know that some people in Band Council put together a game that you can play with others while at Interlochen.

Your password is: {to_password}
Check it out at https://bandwagon.nkrok.io



""")

send = driver.find_element_by_id(":7q")
send.click()
