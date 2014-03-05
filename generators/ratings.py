import csv
import argparse
from collections import defaultdict

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

def is_valid(indata):
  if indata and indata != 'NULL':
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

def usermatrix_to_file(users, filename):
  # Reset the file
  open(filename, 'w').close()

  # Then write our contents to the output file.
  with open(filename, 'a') as output:
    for user_id, products in users.iteritems():
      for product_id, events in products.iteritems():
        rating = translate_events(events)
        output.write("%s\t%s\t%s\n" % (user_id, product_id, rating))



def main():
  parser = argparse.ArgumentParser(description = 'Generate ratings file')
  parser.add_argument('inputfile')
  parser.add_argument('-o', dest='outputfile', default='output.csv')
  args = parser.parse_args()

  users = create_usermatrix(args.inputfile)
  usermatrix_to_file(users, args.outputfile)

if __name__ == '__main__':
  main()
