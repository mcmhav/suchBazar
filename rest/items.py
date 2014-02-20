import requests
import time
import json

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
  print "Starting on collection %s of %s" % (i, total_collections)
  collection_id = collection["id"]

  offers_url = "%s/%s?collectionId=%s" % (base_url, "offer/v10", collection_id)

  # Request the number of items in this collection
  time.sleep(3)
  res = requests.get(offers_url, auth=(username, password))
  json_data = res.json()
  total_size = json_data["totalSize"]

  # Construct new url with all items
  offers_url_complete = "%s&pageSize=%s" % (offers_url, total_size)

  # Request all offers in this collection
  time.sleep(3)
  response = requests.get(offers_url_complete, auth=(username, password))
  json_data = res.json()

  for item in json_data["items"]:
    print "Adding item: %s (%s)" % (item["id"], item["title"])
    items.append(item)

  # Write to file
  f.seek(0)
  f.write(json.dumps(items))

  # Increase counter
  i += 1
