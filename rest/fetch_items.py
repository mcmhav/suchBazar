#!/usr/bin/env python
import urllib2, base64, time, json, sys, os

# Settings
base_url = "https://goodiez-staging.appspot.com/api/goodiez"
username = "goodiez"
password = "goodiez"
increment = 1000
mode = 'file'

# This folder
base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)
output_file = "%s/%s/%s" % (root_dir, 'generated', 'products_json.txt')

def get_empty_mongo_db(db):
  # Reset it and return col-object.
  col = db["items"]
  col.remove()

def get_product_json(offers_url, timeout=3):
  # Request all offers in this collection
  time.sleep(timeout)

  # Make authenticated request
  request = urllib2.Request(offers_url)
  base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
  request.add_header("Authorization", "Basic %s" % base64string)
  res = urllib2.urlopen(request)

  return json.loads(res.read())

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
    import pymongo
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
