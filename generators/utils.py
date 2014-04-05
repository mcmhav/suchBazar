import csv
import numpy as np
from collections import defaultdict

def is_valid(indata):
  if indata and indata not in ('N/A', '-1', 'NULL'):
    return True
  return False

def create_usermatrix(filename):
  # The dictionary containing all events for one user
  users = defaultdict(lambda: defaultdict(list))

  # Read the input .tab file.
  with open(filename) as f:
    for row in csv.reader(f, delimiter='\t'):
      event_id = row[1]
      product_id = row[12]
      user_id = row[16]
      if is_valid(user_id) and is_valid(product_id) and is_valid(event_id):
        users[user_id][product_id].append(event_id)

  return users

def translate_events(events):
  # A list of events.
  multipliers = {
    'featured_product_clicked': [10, 20, 30, 40, 50],
    'product_detail_clicked': [10, 20, 30, 40, 50],
    'product_wanted': [55, 65, 75],
    'product_purchase_intended': [90],
    'product_purchased': [100]
  }
  count = defaultdict(int)
  rating = 0
  for event in events:
    # The number of times we've seen this event for this user
    freq = count[event]

    # Get the multipliers for this event.
    multi = multipliers.get(event, [0])

    # Get the index we will use to get score. Max is length of number of scores.
    idx = min(freq, len(multi)-1)

    # Just get the score. And if it is higher than existing rating, replace it.
    rating = max(rating, multi[idx])

    # Increase the count for this event.
    count[event] += 1

  # Normalize to k
  t = rating
  k = 5.0
  rating = ((k-1)/100.0) * rating + 1

  return rating

def products_to_file(user_id, products, f):
  ratings = []
  for product_id, events in products.iteritems():
    rating = translate_events(events)
    ratings.append(rating)
    if rating > 0:
      f.write("%s\t%s\t%s\n" % (user_id, product_id, rating))
  print "Average: %s, Median: %s" % (np.mean(ratings), np.median(ratings))
