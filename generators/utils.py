import csv
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
    'featured_product_clicked': 1,
    'product_detail_clicked': 1,
    'product_wanted': 5,
    'product_purchase_intended': 10,
    'product_purchased': 15
  }
  rating = 0
  for event in events:
    rating += multipliers.get(event, 0)
  return rating

def products_to_file(user_id, products, f):
  for product_id, events in products.iteritems():
    rating = translate_events(events)
    if rating > 0:
      f.write("%s\t%s\t%s\n" % (user_id, product_id, rating))
