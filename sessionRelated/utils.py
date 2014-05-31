from collections import defaultdict
from datetime import datetime, timedelta

def is_valid(inputs):
  for inp in inputs:
    if not inp or inp in ('N/A', '-1', 'NULL', 'null', 'testimplementation'):
      return False
  return True

def parse_eventline(line, newer_than=0):
  today = datetime.now()

  row = line.split("\t")
  event_id = row[1]
  timestamp = row[3]
  product_id = row[12]
  user_id = row[16]
  if is_valid([event_id, product_id, user_id, timestamp]):
    t = parse_timestamp(timestamp)
    if newer_than > 0:
      if t < (today - timedelta(days=newer_than)):
        return None
    return {"product_id": product_id, "event_id": event_id, "user_id": user_id, "timestamp": parse_timestamp(timestamp)}
  return None

def parse_timestamp(timestamp):
  return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

def read_events(filename, newer_than=0):
  # Dictionary holding users. All users has a dictionary with products.
  users = defaultdict(lambda: defaultdict(list))

  f = open(filename, "r")
  for line in f.readlines():
    event = parse_eventline(line, newer_than)
    if event:
      u = event["user_id"]
      p = event["product_id"]
      users[u][p].append(event)
  return users
