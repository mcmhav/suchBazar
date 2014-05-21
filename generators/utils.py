import csv
import sys
import math
import pymongo
from datetime import datetime
from collections import defaultdict
import operator
import numpy as np

# Dictionary holding the number of days since the most recent event,
# for user i.
last_event = defaultdict(lambda: datetime.min)
oldest_event = defaultdict(lambda: datetime.max)
ignored = 0

def normalize(score,xmax=100,xmin=0,a=0,b=5):
  # From http://en.wikipedia.org/wiki/Normalization_(statistics)#Examples
  return a + (((score-xmin)*(b-a))/(xmax-xmin))

def z_score(x, avg, standard_dev):
  return (x-avg)/standard_dev

def norm_dist(x, avg, standard_dev):
  # Get z-score
  z = z_score(x, avg, standard_dev)

  # We treat negative and positive values equally
  z = math.fabs(z)

  # Cap outliers
  z = min(z, standard_dev)

  # Return relative z-score
  return z/standard_dev

def sigmoid(k, **kwargs):
  if "ratio" in kwargs and "c" in kwargs:
    return sigmoid_c(k, kwargs["ratio"], kwargs["c"])
  if "constant" in kwargs:
    return 1 / (1 + math.exp(-0.2*(k-kwargs["constant"])))

def sigmoid_c(k, ratio, c):
  # http://fooplot.com/#W3sidHlwZSI6MCwiZXEiOiIxLygxK2VeKCgtKDIqNCkvMSkqKHgtKDEvMikpKSkiLCJjb2xvciI6IiMwMDAwMDAifSx7InR5cGUiOjEwMDAsIndpbmRvdyI6WyIwIiwiMSIsIjAiLCIxIl19XQ--
  steep = -(ratio/c)
  shift = (k - c)
  return 1 / (1 + math.exp(steep*shift))

def parse_timestamp(timestamp):
  return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

def calc_most_recent(curr, timestamp):
  t = parse_timestamp(timestamp)
  #diff = today - t
  return min(curr, t)

def is_valid(indata):
  if indata and indata not in ('N/A', '-1', 'NULL', 'null', 'testimplementation'):
    return True
  return False

def parse_eventline(row, users, config):
  event_id = row[1]
  timestamp = row[3]
  product_id = row[12]
  user_id = row[16]
  if is_valid(user_id) and is_valid(product_id) and is_valid(event_id):
    # Parse timestamp
    t = parse_timestamp(timestamp)

    # Check if the event is too old
    if config.get("min_date", None):
      if t < config["min_date"]:
        return
    # Check if it is too recent
    if config.get("max_date", None):
      if t > config["max_date"]:
        return

    users[user_id][product_id].append({'event_id': event_id, 'timestamp': t, 'product_id': product_id, 'user_id': user_id})

    # Most recent event on this item.
    k = "%s-%s" % (user_id, product_id)
    last_event[k] = t if t > last_event[k] else last_event[k]

    # Save the oldest event for this user as well.
    oldest_event[user_id] = t if t < oldest_event[user_id] else oldest_event[user_id]

def parse_mongo(users, config):
  client = pymongo.MongoClient()
  db = client.mydb
  col = db['negValues']
  mongoDB = col.find()
  for instance in mongoDB:
    row = [''] * 17
    row[1] = instance['event_id']
    row[3] = instance['server_time_stamp']
    row[12] = instance['product_id']
    row[16] = instance['user_id'] # 2014-02-03T18:59+0100
    parse_eventline(row, users, config)


def create_usermatrix(config):
  # The dictionary containing all events for one user
  users = defaultdict(lambda: defaultdict(list))
  # Use data from mongo?
  if config["infile"] == "mongo":
    parse_mongo(users, config)
  else:
    # Read the input .tab file.
    with open(config["infile"]) as f:
      if config.get("skipheader", None):
        next(f, None)  # skip the headers
      for row in csv.reader(f, delimiter='\t'):
        parse_eventline(row, users, config)

  return users

def fx_naive(events):
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

def write_ratings_to_file(user_id, ratings, f, config):
  """
    Writes to a file:
      user_id, product_id, rating
  """
  for product_id in sorted(ratings):#.iteritems():
    base = "%s\t%s\t%.3f" % (user_id, product_id, ratings[product_id])#rating)
    if config["timestamps"]:
      f.write("%s\t%s\n" % (base, last_event["%s-%s" % (user_id, product_id)].strftime("%Y-%m-%d %H:%M:%S")))
      continue
    f.write("%s\n" % base)

def get_penalization(n, num, config, average=0.0):
  p = 0

  if num < 2:
    return 0

  # Get penalization from various function schemes
  if config["fx"] == "sigmoid_fixed":
    p = sigmoid(n, ratio=config["sigmoid_ratio"], c=num/2)
  elif config["fx"] == "sigmoid_constant":
    p = sigmoid(n, constant=config["sigmoid_constant"])
  elif config["fx"] == "norm_dist":
    p = norm_dist(n, average, config["norm_standard_dev"])
  elif config["fx"] == "linear":
    p = n/float(num)

  # Round down to zero if the penalization is really small
  THRESHOLD = 0.05
  if (p - int(p)) < THRESHOLD and num < 8:
    p = int(p)
  return p

def get_multipliers():
  return {
    'negative_event': [0,20],
    'featured_product_clicked': [20,60],
    'product_detail_clicked': [20,60],
    'product_wanted': [60,80],
    'product_purchase_intended': [80,100],
    'product_purchased': [80,100]
  }

def get_without_neg_multipliers():
  return {
    'featured_product_clicked': [10,60],
    'product_detail_clicked': [10,60],
    'product_wanted': [60,80],
    'product_purchase_intended': [80,100],
    'product_purchased': [80,100]
  }

def fx_recentness(events, oldest_event, config, rating=0):
  today = datetime.now()
  # Get multipliers and valid events
  multipliers = get_without_neg_multipliers()

  # Remove events which we dont care about.
  events[:] = [d for d in events if d.get('event_id') in multipliers]

  # No valid events? Then we dont return anything.
  if not events:
    return None

  # Special case if we use normal distribution, as we need the average
  avg = 0.0
  if config["fx"] == "norm_dist":
    c = 0
    for event in events:
      t = parse_timestamp(event['timestamp'])
      diff_today = today - t
      diff_event = today - oldest_event
      c += (diff_today.days - diff_event.days)
    avg = c / len(events)

  for event in events:
    t = event['timestamp']

    # The number of days this event is from the latest event for this user.
    diff_event = (today - t).days
    diff_oldest = (today - oldest_event).days

    penalization = get_penalization(diff_event, diff_oldest, config, average=avg)

    # Get the scores for this event type.
    scores = multipliers.get(event['event_id'])

    # Calculate the diff between the scores, and multiply with penalization.
    score = scores[1] - ((scores[1] - scores[0]) * penalization)

    rating = max(rating, normalize(score=score, a=1, b=5.0, xmin=10))
  return rating

def fx_count(events, config, avg_num_events):
  """
    We want to create ratings based on a counting scheme. That it we look at
    all events for all items for one user. Based on function (fx) we return all
    ratings.
  """
  today = datetime.now()
  # Get multipliers and valid events
  multipliers = get_without_neg_multipliers()

  # Remove events which we dont care about.
  events[:] = [d for d in events if d.get('event_id') in multipliers]
  num_events = len(events)

  # We want to sort all events by most recent to oldest.
  events.sort(key=operator.itemgetter('timestamp'), reverse=True)

  ratings = {}
  for i, event in enumerate(events):
    # Calc penalization based on fx
    product_penalization = get_penalization(i, num_events, config, average=avg_num_events)

    if product_penalization < 0.01:
      days_since_event = (today - event["timestamp"]).days
      days_since_oldest = (today - oldest_event[event["user_id"]]).days
      product_penalization = (float(days_since_event) / float(days_since_oldest)) * 0.3

    scores = multipliers.get(event['event_id'])
    score = scores[1] - ((scores[1] - scores[0]) * product_penalization)
    norm_score = normalize(score, a=1, b=5.0, xmin=10)
    r = max(ratings.get(event['product_id'], 0.0), norm_score)
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
    avg = np.mean([len(e) for e in events.iteritems()])
    return fx_count([e for product_id, evt in events.iteritems() for e in evt], config, avg)
  else:
    for product_id, evts in events.iteritems():
      rating = None
      # Get the rating from one of the different calculation schemes.
      if config["method"] == 'recentness':
        rating = fx_recentness(evts, oldest_event[user_id], config)
      elif config["method"] == 'naive':
        rating = fx_naive(evts)
      if rating:
        ratings[product_id] = rating
  return ratings
