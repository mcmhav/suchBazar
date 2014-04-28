import csv
import sys
import math
from datetime import datetime
from collections import defaultdict
from operator import itemgetter

# Dictionary holding the number of days since the most recent event,
# for user i.
mr = defaultdict(lambda: sys.maxint)
ignored = 0

def normalize(score, k):
  return ((k-1)/100.0) * score + 1

def sigmoid(k, **kwargs):
  if "c" in kwargs:
    return sigmoid_c(k, kwargs["c"])
  return 1 / (1 + math.exp(-0.2*(k-30)))

def sigmoid_c(k, c):
  # Some special cases when c is small:
  f = 6
  if c == 1:
    return 0
  if c > 2:
    f = 5/c
  return 1 / (1 + math.exp(-f*(k-c)))

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
    mr[user_id] = calc_most_recent(mr[user_id], timestamp, today)

def create_usermatrix(filename):
  # The dictionary containing all events for one user
  users = defaultdict(lambda: defaultdict(list))

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
    rating = max(rating, normalize(multi[idx], 5.0))

    # Increase the count for this event.
    count[event['event_id']] += 1
  return rating

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

    rating = max(rating, normalize(score, 5.0))
  return rating

def sigmoid_count(events):
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
  events = sorted(events, key=itemgetter('timestamp'), reverse=True)

  num_events = len(events)

  ratings = {}
  for i, event in enumerate(events):
    product_penalization = sigmoid((i+1), c=num_events)
    scores = multipliers.get(event['event_id'])
    score = scores[1] - ((scores[1] - scores[0]) * product_penalization)

    r = max(ratings.get(event['product_id'], 0.0), normalize(score, 5.0))
    ratings[event['product_id']] = r
  return ratings

def products_to_file(user_id, products, f, method):
  """
    Writes to a file:
       user_id, product_id, rating

    Input is all products than has an event, for user_id.
    Thus, this function is typically run inside a loop for all users in the system.

    The returned ratings array is just an array we use in order to calculate the
    final average in the end of the program.
  """
  ratings = []

  if method == 'scount':
    e = []
    for product_id, events in products.iteritems():
      e.extend(events)
    rts = sigmoid_count(e)

    for product_id, rating in rts.iteritems():
      f.write("%s\t%s\t%.2f\n" % (user_id, product_id, rating))
      ratings.append(rating)
  else:
    for product_id, events in products.iteritems():

      # Get the rating from one of the different calculation schemes.
      rating = 1.0
      if method == 'srecent':
        rating = sigmoid_events(events, mr[user_id])
      elif method == 'naive':
        rating = translate_events(events)
      ratings.append(rating)

      f.write("%s\t%s\t%.2f\n" % (user_id, product_id, rating))
    return ratings
  return ratings
