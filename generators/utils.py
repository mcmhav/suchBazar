import csv
import sys
import math
import pymongo
from datetime import datetime
from collections import defaultdict
from operator import itemgetter

# Dictionary holding the number of days since the most recent event,
# for user i.
days_last_event = defaultdict(lambda: sys.maxsize)
ignored = 0

def normalize(score,xmax=100,xmin=0,a=0,b=5):
  # From http://en.wikipedia.org/wiki/Normalization_(statistics)#Examples
  return a + (((score-xmin)*(b-a))/(xmax-xmin))

def sigmoid(k, **kwargs):
  if "ratio" in kwargs and "c" in kwargs:
    return sigmoid_c(k, kwargs["ratio"], kwargs["c"])
  if "constant" in kwargs:
    return 1 / (1 + math.exp(-0.2*(k-kwargs["constant"])))

def sigmoid_c(k, ratio, c):
  # http://fooplot.com/#W3sidHlwZSI6MCwiZXEiOiIxLygxK2VeKCgtKDIqNCkvMSkqKHgtKDEvMikpKSkiLCJjb2xvciI6IiMwMDAwMDAifSx7InR5cGUiOjEwMDAsIndpbmRvdyI6WyIwIiwiMSIsIjAiLCIxIl19XQ--
  steep = -((2*ratio)/c)
  shift = k - (c/2.0)
  return 1 / (1 + math.exp(steep*shift))

def parse_timestamp(timestamp):
  return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

def calc_most_recent(curr, timestamp, today):
  t = parse_timestamp(timestamp)
  diff = today - t
  return min(curr, diff.days)

def is_valid(indata):
  if indata and indata not in ('N/A', '-1', 'NULL', 'null', 'testimplementation'):
    return True
  return False

def parse_eventline(row, users):
  today = datetime.now()
  event_id = row[1]
  timestamp = row[3]
  product_id = row[12]
  user_id = row[16]
  if is_valid(user_id) and is_valid(product_id) and is_valid(event_id):
    users[user_id][product_id].append({'event_id': event_id, 'timestamp': timestamp, 'product_id': product_id})
    days_last_event[user_id] = calc_most_recent(days_last_event[user_id], timestamp, today)

def parse_mongo(users):
  client = pymongo.MongoClient()
  db = client.mydb
  col = db['cleanedItems']
  mongoDB = col.find()
  for instance in mongoDB:
    row = [''] * 17
    row[1] = instance['event_id']
    row[3] = instance['server_time_stamp']
    row[12] = instance['product_id']
    row[16] = instance['user_id'] # 2014-02-03T18:59+0100
    parse_eventline(row,users)


def create_usermatrix(filename):
  # The dictionary containing all events for one user
  users = defaultdict(lambda: defaultdict(list))
  # Use data from mongo?
  if filename == "mongo":
    parse_mongo(users)
  else:
    # Read the input .tab file.
    with open(filename) as f:
      next(f, None)  # skip the headers
      for row in csv.reader(f, delimiter='\t'):
        parse_eventline(row, users)

  return users

def translate_events(events):
  # A list of events.
  multipliers = {
    'featured_product_clicked': [30, 40, 50, 60, 70],
    'product_detail_clicked': [30, 40, 50, 60, 70],
    'product_wanted': [80],
    'product_purchase_intended': [100],
    'product_purchased': [100]
  }
  count = defaultdict(int)
  rating = 0
  for event in events:
    if not event['event_id'] in multipliers:
      global ignored
      ignored += 1
      continue
    # The number of times we've seen this event for this user
    freq = count[event['event_id']]

    # Get the multipliers for this event.
    multi = multipliers.get(event['event_id'])

    # Get the index we will use to get score. Max is length of number of scores.
    idx = min(freq, len(multi)-1)

    # Just get the score. And if it is higher than existing rating, replace it.
    # and normalize to k
    rating = max(rating, normalize(score=multi[idx], a=0, b=5))

    # Increase the count for this event.
    count[event['event_id']] += 1
  return rating

def translate_global(events):
  pass

def sigmoid_events(events, d):
  multipliers = {
    'featured_product_clicked': [10,60],
    'product_detail_clicked': [10,60],
    'product_wanted': [60,80],
    'product_purchase_intended': [80,100],
    'product_purchased': [80,100]
  }
  today = datetime.now()
  rating = 0
  for event in events:
    if not event['event_id'] in multipliers:
      global ignored
      ignored += 1
      continue
    t = parse_timestamp(event['timestamp'])
    diff = today - t

    # The number of days this event is from the latest event for this user.
    relative_diff = diff.days - d

    penalization = sigmoid(relative_diff)

    # Get the scores for this event type.
    scores = multipliers.get(event['event_id'])

    # Calculate the diff between the scores, and multiply with penalization.
    score = scores[1] - ((scores[1] - scores[0]) * penalization)

    rating = max(rating, normalize(score=score, a=1, b=5.0))
  return rating

def sigmoid_count(events):
  """
    Input is all events related to user u.
    Output is the ratings for this all items the user has interacted with.
  """
  multipliers = {
    'featured_product_clicked': [10,60],
    'product_detail_clicked': [10,60],
    'product_wanted': [60,80],
    'product_purchase_intended': [80,100],
    'product_purchased': [80,100]
  }

  # Remove events which we dont care about.
  events[:] = [d for d in events if d.get('event_id') in multipliers]

  # We want to sort all events by most recent to oldest.
  events = sorted(events, key=itemgetter('timestamp'), reverse=False)

  num_events = len(events)

  ratings = {}
  for i, event in enumerate(events):
    product_penalization = sigmoid(i, c=num_events)
    scores = multipliers.get(event['event_id'])
    score = scores[1] - ((scores[1] - scores[0]) * product_penalization)
    r = max(ratings.get(event['product_id'], 0.0), normalize(score=score, a=0, b=5.0))
    ratings[event['product_id']] = r
  return ratings

def write_ratings_to_file(user_id, ratings, f):
  """
    Writes to a file:
      user_id, product_id, rating
  """
  for product_id, rating in ratings.items():
    f.write("%s\t%s\t%.3f\n" % (user_id, product_id, rating))

def get_penalization(n, num, config):
  if config["fx"] == "sigmoid_fixed":
    return sigmoid(n, ratio=config["sigmoid_ratio"], c=num)
  elif config["fx"] == "sigmoid_constant":
    return sigmoid(n, constant=config["sigmoid_constant"])
  else:
    return n/float(num)

def get_multipliers():
  return {
    'featured_product_clicked': [10,60],
    'product_detail_clicked': [10,60],
    'product_wanted': [60,80],
    'product_purchase_intended': [80,100],
    'product_purchased': [80,100]
  }

def fx_recentness(events, oldest_event, config, rating=0):
  today = datetime.now()
  num_events = len(events)

  # Get multipliers and valid events
  multipliers = get_multipliers()

  # Remove events which we dont care about.
  events[:] = [d for d in events if d.get('event_id') in multipliers]

  for event in events:
    t = parse_timestamp(event['timestamp'])
    diff = today - t

    # The number of days this event is from the latest event for this user.
    relative_diff = diff.days - oldest_event

    penalization = get_penalization(relative_diff, oldest_event, config)

    # Get the scores for this event type.
    scores = multipliers.get(event['event_id'])

    # Calculate the diff between the scores, and multiply with penalization.
    score = scores[1] - ((scores[1] - scores[0]) * penalization)

    rating = max(rating, normalize(score=score, a=1, b=5.0))
  return rating

def fx_count(events, config):
  """
    We want to create ratings based on a counting scheme. That it we look at
    all events for all items for one user. Based on function (fx) we return all
    ratings.
  """
  # Get multipliers and valid events
  multipliers = get_multipliers()

  # Remove events which we dont care about.
  events[:] = [d for d in events if d.get('event_id') in multipliers]

  # We want to sort all events by most recent to oldest.
  events = sorted(events, key=itemgetter('timestamp'), reverse=False)

  num_events = len(events)

  ratings = {}
  for i, event in enumerate(events):
    # Calc penalization based on fx
    product_penalization = get_penalization(i, num_events, config)
    scores = multipliers.get(event['event_id'])
    score = scores[1] - ((scores[1] - scores[0]) * product_penalization)
    r = max(ratings.get(event['product_id'], 0.0), normalize(score=score, a=0, b=5.0))
    ratings[event['product_id']] = r
  return ratings

def get_ratings_from_user(user_id, events, f, config):
  """
    Generates a list of ratings for user_id, based on events in products.

    Input is all products than has an event, for user_id.
    Thus, this function is typically run inside a loop for all users in the system.

    The returned ratings array is just an array we use in order to calculate the
    final average in the end of the program.
  """
  ratings = {}
  if config["method"] == 'count':
    # This method needs to work on all events for all items that this user has
    # interacted on, and not one and one product_id. Thus, handle all events in
    # one array.
    return fx_count([e for product_id, evt in events.iteritems() for e in evt], config)
  else:
    for product_id, evts in events.items():
      # Get the rating from one of the different calculation schemes.
      if config["method"] == 'recentness':
        rating = fx_recentness(evts, days_last_event[user_id], config)
      elif config["method"] == 'naive':
        rating = translate_events(evts)
      ratings[product_id] = rating
  return ratings
