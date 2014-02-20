import requests
import time
import json
import sys
import pymongo

# Settings
base_url = "https://goodiez-staging.appspot.com/api/goodiez"
username = "goodiez"
password = "goodiez"
pageSize = 1000
increment = 500
cursorKey = None

# Mongo.db
client = pymongo.MongoClient()
db = client.mydb
col = db["items"]
col.remove()

while pageSize < 20000:
  # Increase counter and give status to user
  print "Getting offer %s to %s" % (pageSize, pageSize + increment)
  pageSize += increment

  offers_url = "%s/%s?pageSize=%s" % (base_url, "offer/v10", increment)
  if cursorKey:
    offers_url = "%s&cursorKey=%s" % (offers_url, cursorKey)

  # Request all offers in this collection
  time.sleep(3)
  res = requests.get(offers_url, auth=(username, password))
  if res.status_code != 200:
    print "Recieved status: %s, skipping." % res.status_code
    continue
  jdata = res.json()

  # Save the cursor key
  cursorKey = jdata["cursorKey"]

  for item in jdata["items"]:
    col.insert(item)
