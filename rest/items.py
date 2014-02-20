import requests
import time
import json
import sys

# Settings
base_url = "https://goodiez-staging.appspot.com/api/goodiez"
total_collections = 87
username = "goodiez"
password = "goodiez"
output_file = "items.json"
i = 1

# Open a file for writing
f = open(output_file, "w")

# Load collections
collections_url = "%s/%s?pageSize=%s" % (base_url, 'collection/v10', total_collections)
res = requests.get(collections_url, auth=(username, password))
json_data = res.json()

# Find items
items = []

for collection in json_data["items"]:
  # Increase counter and give status to user
  print "Starting on collection %s of %s" % (i, total_collections)
  i += 1

  collection_id = collection["id"]

  offers_url = "%s/%s?collectionId=%s" % (base_url, "offer/v10", collection_id)

  # Default to a large pageSize, in order to get alle items.
  total_size = 1000

  # Construct new url with all items
  offers_url_complete = "%s&pageSize=%s" % (offers_url, total_size)

  # Request all offers in this collection
  time.sleep(3)
  res = requests.get(offers_url_complete, auth=(username, password))
  if res.status_code != 200:
    print "Recieved status: %s, skipping." % res.status_code
    continue
  jdata = res.json()

  print "Got collection id %s, found %s items. Adding ..." % (collection_id, jdata.get("totalSize", -1))

  for item in jdata["items"]:
    items.append(item)

  # Write to file
  f.seek(0)
  f.write(json.dumps(items))
