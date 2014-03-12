import requests
import time
import json
import sys
import argparse
import pymongo

parser = argparse.ArgumentParser(description='Crawl the API db.')
parser.add_argument('-v',dest='v', action='store_true')
parser.add_argument('-f',type=str, default="offer")
parser.add_argument('-version',type=str, default="v10")
parser.add_argument('-e',type=str, default="staging")
parser.set_defaults(v=False)
args = parser.parse_args()

# Settings
base_url = "https://goodiez-" + args.e + ".appspot.com/api/goodiez"
username = "goodiez"
password = "goodiez"
pageSize = 500
current  = 0
cursorKey = 0

# Mongo.db
client = pymongo.MongoClient()
db = client.mydb
col = db[args.f + args.e0]
col.remove()

while cursorKey or not current:
  # Increase counter and give status to user
  print ("Getting %s %s to %s" % (args.f, current, current + pageSize))
  current += pageSize

  offers_url = "%s/%s?pageSize=%s" % (base_url, args.f + "/" + args.version, pageSize)
  if cursorKey:
    offers_url = "%s&cursorKey=%s" % (offers_url, cursorKey)

  # print (offers_url)
  # Request all offers in this collection
  time.sleep(3)
  res = requests.get(offers_url, auth=(username, password))
  if res.status_code != 200:
    print ("Recieved status: %s, skipping." % res.status_code)
    continue
  jdata = res.json()

  # Save the cursor key
  if 'cursorKey' in jdata:
    cursorKey = jdata["cursorKey"]
  else:
    cursorKey = 0

  for item in jdata["items"]:
    col.insert(item)
