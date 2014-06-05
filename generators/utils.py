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
oldest_event_globally = defaultdict(lambda: datetime.max)
most_recent_globally = defaultdict(lambda: datetime.min)
product_popularity = defaultdict(float)
product_count = defaultdict(int)
avg_popularity = 0.0

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
    return 1 / (1 + math.exp(-0.15*(k-kwargs["constant"])))

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
  price = row[10]
  product_id = row[12]
  user_id = row[16]
  if is_valid(user_id) and is_valid(product_id) and is_valid(event_id) and is_valid(price):
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

    users[user_id][product_id].append({
      'event_id': event_id,
      'timestamp': t,
      'product_id': product_id,
      'user_id': user_id,
      'price': float(price)
    })

    # Most recent event on this item.
    k = "%s-%s" % (user_id, product_id)
    last_event[k] = t if t > last_event[k] else last_event[k]

    # Save the oldest event for this user as well.
    oldest_event[user_id] = t if t < oldest_event[user_id] else oldest_event[user_id]

    # global oldest_event_globally
    oldest_event_globally[event_id] = t if t < oldest_event_globally[event_id] else oldest_event_globally[event_id]

    # global most_recent_globally
    most_recent_globally[event_id] = t if t > most_recent_globally[event_id] else most_recent_globally[event_id]

def parse_mongo(users, config):
  client = pymongo.MongoClient()
  db = client.mydb
  col = db['sessionsNew']
  mongoDB = col.find()
  for instance in mongoDB:
    row = [''] * 17
    row[1] = instance['event_id']
    row[3] = instance['server_time_stamp']
    row[10] = instance['price']
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
    'negative_event': [10],
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
      # f.write("%s\t%s\n" % (base, last_event["%s-%s" % (user_id, product_id)].strftime("%Y-%m-%d %H:%M:%S")))
      f.write("%s\t%s\n" % (base, last_event["%s-%s" % (user_id, product_id)].strftime("%s")))
      continue
    f.write("%s\n" % base)

def get_penalization(n, num, config, average=0.0, median=None):
  p = 0

  if num < 2:
    return 0

  # Get penalization from various function schemes
  if config["fx"] == "sigmoid_fixed":
    p = sigmoid(n, ratio=config["sigmoid_ratio"], c=num/2.0)
  elif config["fx"] and median:
    p = sigmoid(n, constant=median)
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
    # 'negative_event': [0,4],
    # 'featured_product_clicked': [20,60],
    'product_detail_clicked': [0,62],
    'product_wanted': [62,95],
    'product_purchase_intended': [95,100],
    # 'product_purchased': [80,100]
  }

def get_without_neg_multipliers():
  return {
    # 'featured_product_clicked': [0,60],
    'product_detail_clicked': [0,62],
    'product_wanted': [62,95],
    'product_purchase_intended': [95,100],
    # 'product_purchased': [80,100]
  }

def fx_recentness(events, config, rating=0, median=None):
  # today = datetime.now()
  # Get multipliers and valid events
  if config["infile"] == "mongo":
    multipliers = get_multipliers()
  else:
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
    most_recent_global = most_recent_globally[event["event_id"]]
    oldest_global = oldest_event_globally[event["event_id"]]
    oldest_user = oldest_event[event["user_id"]]

    # The number of days this event is from the latest event for this user.
    oldest = (most_recent_global - oldest_user).days
    diff_event = (most_recent_global - t).days
    if config["minmax"] != "user":
      oldest = (most_recent_global - oldest_global).days

    penalization = get_penalization(diff_event, oldest, config, average=avg, median=median)

    # Get the scores for this event type.
    scores = multipliers.get(event['event_id'])

    # Calculate the diff between the scores, and multiply with penalization.
    score = scores[1] - ((scores[1] - scores[0]) * penalization)

    # Get the min multiplier in the multiplier set
    xmin = findMinMultiplier(multipliers)

    rating = max(rating, normalize(score=score, a=1, b=5.0, xmin=xmin))
  return rating

def findMinMultiplier(multipliers):
  '''
  Find the minimum value of all the multipliers
  '''
  mV = min(multipliers, key=multipliers.get)
  m = multipliers[mV][0]
  return m

def fx_count(events, config, avg_num_events):
  """
    We want to create ratings based on a counting scheme. That it we look at
    all events for all items for one user. Based on function (fx) we return all
    ratings.
  """
  today = datetime.now()
  # Get multipliers and valid events
  if config["infile"] == "mongo":
    multipliers = get_multipliers()
  else:
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
    xmin = findMinMultiplier(multipliers)
    norm_score = normalize(score, a=1, b=5.0, xmin=xmin)
    r = max(ratings.get(event['product_id'], 0.0), norm_score)
    ratings[event['product_id']] = r
  return ratings

def init_calc(users):
  # First pass, count products.
  for uid, products in users.iteritems():
    for pid, events in products.iteritems():
      product_count[pid] += 1

  # Sort by count, as list of tuples.
  sorted_prodcount = sorted(product_count.iteritems(), key=operator.itemgetter(1))
  num_products = float(len(product_count))

  for i, product in enumerate(sorted_prodcount):
    pid = product[0]
    product_popularity[pid] = i / num_products

  # Second pass, find average popularity
  popularities = []
  for uid, products in users.iteritems():
    for pid, events in products.iteritems():
      for e in events:
        p = product_popularity[pid]
        popularities.append(p)

  global avg_popularity
  avg_popularity = np.average(popularities)
  print "Set avg_popularity to %.4f" % avg_popularity

def get_popularity_rating(pop):
  """
    Returns a number between 0 and rmax.
  """
  # a = -12.353336986688191
  # b = 19.272762696836708
  # c = -9.49625639913711
  # d = 2.0931143246693296
  # e = 0.48841143839214785
  # f = a * math.pow(pop, 4) + b * math.pow(pop, 3) + c * math.pow(pop, 2) + d * pop + e
  # return max(f,0.0)
  best_item_score = 0.5
  if pop < avg_popularity:
    return - (best_item_score / avg_popularity) * pop + best_item_score
  increase = 1/(1-avg_popularity)
  return increase * pop - increase + 1

def fx_popularity(events, config):
  MAX_RATING = 5.0
  MIN_RATING = 1.0

  rating = 0.0
  for event in events:
    pid = event["product_id"]

    pop = product_popularity[pid]
    penalization = get_popularity_rating(pop)
    r = MAX_RATING - (MAX_RATING - MIN_RATING) * penalization
    norm_rating = normalize(r,a=1.0,b=5.0,xmin=1.0,xmax=5.0)
    rating = max(rating, norm_rating)
    if rating == 1.0:
      print pop, penalization, r, rating
  return rating

def get_price_penalization(diff, maxprice):
  # Do not penalize being cheap, that much.
  if diff < 0:
    diff = abs(diff)/2

  p = min(1, diff/maxprice)
  return p

def fx_price(events, config):
  # Max penalization price
  MAX_PEN_PRICE = 1500
  MAX_SCORE = 100
  MIN_SCORE = 0

  # First find average price for all items that this user has interacted on.
  # Hence, we need to first group by product.
  products = {}
  for event in events:
    products[event["product_id"]] = event["price"]
  avg_price = np.average(products.values())

  # Then for each product find penalization based on difference in price to the avg.
  ratings = {}
  for event in events:
    product_id = event["product_id"]
    price = event["price"]

    diff = price - avg_price
    penalization = get_price_penalization(diff, MAX_PEN_PRICE)
    score = MAX_SCORE - ((MAX_SCORE - MIN_SCORE) * penalization)

    norm_score = normalize(score,a=1,b=5,xmin=MIN_SCORE,xmax=MAX_SCORE)
    r = max(ratings.get(product_id, 0), norm_score)
    ratings[product_id] = r
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
  today = datetime.now()
  if config["method"] in ('count', 'price'):
    # This method needs to work on all events for all items that this user has
    # interacted on, and not one and one product_id. Thus, handle all events in
    # one array.
    avg = np.mean([len(e) for e in events.items()])
    events = [e for product_id, evt in events.items() for e in evt]
    if config["method"] == "count":
      return fx_count(events, config, avg)
    return fx_price(events, config)
  else:

    median = None
    if config.get("sigmoid_constant_average", None):
      day_diffs = [(today - e["timestamp"]).days for pid, evts in events.iteritems() for e in evts]
      median = np.average(day_diffs)

    for product_id, evts in events.items():
      rating = None
      # Get the rating from one of the different calculation schemes.
      if config["method"] == 'recentness':
        rating = fx_recentness(evts, config, median=median)
      elif config["method"] == 'naive':
        rating = fx_naive(evts)
      elif config["method"] == 'popularity':
        rating = fx_popularity(evts, config)
      if rating:
        ratings[product_id] = rating
  return ratings
