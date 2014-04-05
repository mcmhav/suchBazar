#!/usr/bin/env python
import argparse
import numpy as np

import utils

def usermatrix_to_file(users, filename, sigmoid):
  # Reset the file
  open(filename, 'w').close()

  # Then write our contents to the output file.
  ratings = []
  with open(filename, 'a') as output:
    for user_id, products in users.iteritems():
      r = utils.products_to_file(user_id, products, output, sigmoid)
      ratings.extend(r)
  print "Average: %s, Median: %s" % (np.mean(ratings), np.median(ratings))

def main():
  parser = argparse.ArgumentParser(description = 'Generate ratings file')
  parser.add_argument('inputfile')
  parser.add_argument('-o', dest='outputfile', default='output.csv')
  parser.add_argument('-s', dest='sigmoid', action='store_true', default=False)
  args = parser.parse_args()

  users = utils.create_usermatrix(args.inputfile)
  usermatrix_to_file(users, args.outputfile, args.sigmoid)

if __name__ == '__main__':
  main()
