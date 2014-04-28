#!/usr/bin/env python
import sys
import argparse
from collections import defaultdict
import numpy as np

def read_config(fname):
  config = { 'files' : []}
  f = open(fname)

  lines = list(line for line in (l.strip() for l in f) if line)

  # Ensure we have more than 1 file to blend.
  if len(lines) < 2:
    print "Error: we need more than one file in the config file to blend"
    sys.exit(1)
  f.seek(0)

  # Read the config and open the file handlers
  for l in lines:
    args = l.split()
    fh = open(args[0])
    ratio = float(args[1])
    config['files'].append({ 'fh': fh, 'ratio': ratio })
  f.seek(0)

  # Check that ratios add up to 1.
  s = 0
  for rfile in config['files']:
    s += rfile['ratio']
  if abs(s - 1.0) > 0.000000001:
    print "Error: ratios does not add up to 1.0"
    sys.exit(1)
  f.seek(0)

  # Check that the line numbers in all files are equal.
  r = len(config["files"][0]["fh"].readlines())
  for rfile in config["files"][1:]:
    if len(rfile["fh"].readlines()) != r:
      print "Line numbers in various files does not match"
      sys.exit(1)

  # Reset filehandles for all rating files
  for rfile in config["files"]:
    rfile["fh"].seek(0)

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
  parser.add_argument('-c', dest='conf', default="files.conf", help="Config file for how to linearly weight the different ratings")
  parser.add_argument('-d', dest='dest', default="ratings", help="Where should the blended file be put? Default to: 'ratings'")
  parser.add_argument('-o', dest='filename', default='blend.txt', help="Filename for the blended result. Default to: 'blend.txt'")
  args = parser.parse_args()

  # Add the directory + filename
  args.dest = args.dest + '/' + args.filename

  conf = read_config(args.conf)

  # Data structure holding all information about all ratings for a user.
  users = defaultdict(lambda: defaultdict(int))

  # Do the blending.
  for rfile in conf["files"]:
    blend(users, rfile["fh"], rfile["ratio"])

  # Data structures for statistics
  num_ratings = 0
  ratings = []

  # Write the output-file.
  out = open(args.dest, "w+")
  for user_id, product in users.iteritems():
    for product_id, rating in product.iteritems():
      out.write("%s\t%s\t%s\n" % (user_id, product_id, rating))

      # Save for statistics
      num_ratings += 1
      ratings.append(rating)

  # Close all open files
  for rfile in conf["files"]:
    rfile["fh"].close()

  # Write back to the user
  print "Wrote %d ratings to %s. Average: %.4f,  Median: %.4f" % (num_ratings, args.dest, np.average(ratings), np.median(ratings))
