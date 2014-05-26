#!/usr/bin/env python
import requests
import time
import json
import sys
import pymongo

# Settings
base_url = "https://goodiez-staging.appspot.com/api/goodiez"
username = "goodiez"
password = "goodiez"
increment = 1000
mode = 'file'
output_file = 'products.txt'

def get_empty_mongo_db(db):
  # Reset it and return col-object.
  col = db["items"]
  col.remove()

def get_product_json(offers_url, timeout=3):
  # Request all offers in this collection
  time.sleep(timeout)
  res = requests.get(offers_url, auth=(username, password))
  if res.status_code != 200:
    return res.json()
  return res.json()

def get_offer_url(increment, cursor_key):
  offers_url = "%s/%s?pageSize=%s" % (base_url, "offer/v10", increment)
  if cursor_key:
    offers_url = "%s&cursorKey=%s" % (offers_url, cursor_key)
  return offers_url

def get_filehandler(filename):
  # First reset the file
  open(filename, 'w').close()
  return open(filename, 'a')

def insert_item(f, col, item):
  if col:
    col.insert(item)
    return
  f.write('%s\n' % json.dumps(item))

def sniff_page_size(offers_url):
  jdata = get_product_json(offers_url, timeout=0)
  return jdata.get("totalSize", 0)

def main():
  f, col, cursor_key, current = None, None, None, 0
  if mode == 'mongo':
    # Open mongo-db connection
    client = pymongo.MongoClient()
    col = get_empty_mongo_db(client.db)
  else:
    f = get_filehandler(output_file)

  offers_url = get_offer_url(1, cursor_key)
  page_size = sniff_page_size(offers_url)

  while current < page_size:
    # Increase counter and give status to user
    print ("Getting offer %s to %s (total: %s)" % (current, current + increment, page_size))
    current += increment

    # Create an offer URL.
    offers_url = get_offer_url(increment, cursor_key)

    # Get the data from API.
    jdata = get_product_json(offers_url)
    if not jdata:
      print ("Recieved: %s. Skipping." % jdata)
      continue

    # Save the items
    for item in jdata["items"]:
      insert_item(f, col, item)

    # Save the cursor key, in order to pagination.
    cursor_key = jdata.get("cursorKey", None)
    if not cursor_key:
      print ("Did not recieve cursor key. Exiting.")
      break

  if f:
    # Dont forget to close the file after use.
    f.close()

if __name__ == '__main__':
  main()
