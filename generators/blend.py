#!/usr/bin/env python
import sys
import argparse
from collections import defaultdict

def read_config(fname):
  config = { 'files' : []}
  f = open(fname)

  # Ensure we have more than 1 file to blend.
  if len(f.readlines()) < 2:
    print "Error: we need more than one file in the config file to blend"
    sys.exit(1)
  f.seek(0)

  # Read the config and open the file handlers
  for l in f.readlines():
    args = l.split()
    fh = open(args[0])
    ratio = float(args[1])
    config['files'].append({ 'fh': fh, 'ratio': ratio })
  f.seek(0)

  # Check that ratios add up to 1.
  s = 0
  for rfile in config['files']:
    s += rfile['ratio']
  if s != 1.0:
    print "Error: ratios does not add up to 1.0"
    sys.exit(1)
  f.seek(0)

  # Check that the line numbers in all files are equal.
  r = config["files"][0]["ratio"]
  for rfile in config["files"][1:]:
    if rfile["ratio"] != r:
      print "Line numbers in various files does not match"
      sys.exit(1)

  # And close the config file at the end.
  f.close()

  return config

def blend(users, f, ratio):
  for l in f.readlines():
    # Read in all ratings from the given file.
    args = l.split('\t')
    user_id = args[0]
    product_id = args[1]
    rating = float(args[2])

    # A linear blend, so we calculate the part for this rating.
    rating *= ratio

    # Blend into our data-structure
    current_rating = users[user_id][product_id]
    users[user_id][product_id] = current_rating + rating

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = 'Blend ratings')
  parser.add_argument('-c', dest='conf', default="files.conf")
  parser.add_argument('-d', dest='dest', default='ratings.csv')
  args = parser.parse_args()

  conf = read_config(args.conf)

  # Data structure holding all information about all ratings for a user.
  users = defaultdict(lambda: defaultdict(int))

  # Do the blending.
  for rfile in conf["files"]:
    blend(users, rfile["fh"], rfile["ratio"])

  # Write the output-file.
  out = open(args.dest, "w+")
  for user_id, product in users.iteritems():
    for product_id, rating in product.iteritems():
      out.write("%s\t%s\t%s\n" % (user_id, product_id, rating))

  # Close all open files
  for rfile in conf["files"]:
    rfile["fh"].close()
