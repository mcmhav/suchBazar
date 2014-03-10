import requests
import time
import json
import sys
import pymongo
import psycopg2

# Settings
base_url = "https://goodiez-staging.appspot.com/api/goodiez"
username = "goodiez"
password = "goodiez"
current = 0
increment = 1000
cursorKey = None

# Mongo.db
client = pymongo.MongoClient()
db = client.mydb
col = db["items"]
col.remove()

# Postgresql
"""
conn = psycopg2.connect("dbname=products user=postgres")
cur = conn.cursor()
"""

while current < 45000:
  # Increase counter and give status to user
  print "Getting offer %s to %s" % (current, current + increment)
  current += increment

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

  for item in jdata["items"]:
    col.insert(item)
    #cur.execute("INSERT INTO products(")
  
  # Save the cursor key
  try:
    cursorKey = jdata["cursorKey"]
  except:
    print "Did not recieve cursor key. Exiting."
    break
