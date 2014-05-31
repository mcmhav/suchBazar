#!/usr/bin/env python
#
# Blending-tool for Sobazar and master thesis 2014
# Input: a config-file (list of files) and optionally their ratios
# Output: a linear blend of the average ratings weighted by ratio, of all files.
#
# Rating files should be on the following format:
# user_id \t product_id \t rating [ \t timestamp]
#
# That is a tab-seperated list of (user, product, rating) and optionally the
# timestamp of the rating.
####
import sys, os
import argparse
from collections import defaultdict
import numpy as np

def read_config(fname, rfolder):
  config = { 'files' : []}
  f = open(fname)
  rel_path = os.path.dirname(f.name)

  lines = list(line for line in (l.strip() for l in f) if line)

  # Ensure we have more than 1 file to blend.
  if len(lines) < 2:
    print ("Error: we need more than one file in the config file to blend")
    sys.exit(1)
  f.seek(0)

  # Check if ratios are defined or if we should add them automatically.
  auto = False
  if len(lines[0].split()) == 1:
    auto = True
  num_files = len(lines)

  # Read the config and open the file handlers
  for i, l in enumerate(lines):
    args = l.split()
    fh = open("%s/%s/%s" % (rel_path, rfolder, args[0]))
    ratio = float(args[1]) if not auto else 1/float(num_files)
    config['files'].append({ 'fh': fh, 'ratio': ratio })
  f.seek(0)

  # Check that ratios add up to 1.
  s = 0
  for rfile in config['files']:
    s += rfile['ratio']
  if abs(s - 1.0) > 0.000000001:
    print ("Error: ratios does not add up to 1.0")
    sys.exit(1)
  f.seek(0)

  # Check that the line numbers in all files are equal.
  r = len(config["files"][0]["fh"].readlines())
  for rfile in config["files"][1:]:
    if len(rfile["fh"].readlines()) != r:
      print ("Line numbers in various files does not match")
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
    user_id = args[0].strip()
    product_id = args[1].strip()
    rating = float(args[2].strip())

    timestamp = ""
    if len(args) > 3:
      timestamp = args[3].strip()

    # A linear blend, so we calculate the part for this rating.
    rating *= ratio

    # Blend into our data-structure
    current_rating = users[user_id][product_id].get("rating", 0.0)
    new_rating = current_rating + rating

    # Add to datastructure
    users[user_id][product_id] = {'rating': new_rating, 'timestamp': timestamp}

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = 'Blend ratings')
  parser.add_argument('-c', dest='conf', default="files.conf", help="Config file for how to linearly weight the different ratings")
  parser.add_argument('-d', dest='dest', default="ratings", help="Where should the blended file be put? Default to: 'ratings'")
  parser.add_argument('-i', dest='rfolder', default="ratings", help="Where to find all files defined in conf file")
  parser.add_argument('-o', dest='filename', default='blend.txt', help="Filename for the blended result. Default to: 'blend.txt'")
  args = parser.parse_args()
  abs_path = os.path.dirname(os.path.realpath(__file__))

  # Add the directory + filename
  if args.dest[0] != '/':
    args.dest = abs_path + '/' + args.dest
  args.dest += '/' + args.filename

  conf = read_config(args.conf, args.rfolder)

  # Data structure holding all information about all ratings for a user.
  users = defaultdict(lambda: defaultdict(lambda: defaultdict()))

  # Do the blending.
  for rfile in conf["files"]:
    blend(users, rfile["fh"], rfile["ratio"])

  # Data structures for statistics
  num_ratings = 0
  ratings = []

  # Write the output-file.
  out = open(args.dest, "w+")
  for user_id, product in users.items():
    for product_id, u_p_obj in product.items():
      rating = u_p_obj["rating"]
      timestamp = u_p_obj.get("timestamp", "")

      # Create the output string
      s = "%s\t%s\t%s" % (user_id, product_id, rating)
      if timestamp:
        s += "\t%s" % timestamp

      # Write to file
      out.write("%s\n" % s)

      # Save for statistics
      num_ratings += 1
      ratings.append(rating)

  # Close all open files
  for rfile in conf["files"]:
    rfile["fh"].close()

  # Write back to the user
  print ("Wrote %d ratings to %s. Average: %.4f,  Median: %.4f" % (num_ratings, args.dest, np.average(ratings), np.median(ratings)))
