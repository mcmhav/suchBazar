#!/usr/bin/env python
import argparse
from collections import defaultdict
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
  parser.add_argument('-m', dest='method', default='sigmoid')
  parser.add_argument('-d', dest='debug', action='store_true', default=False)
  args = parser.parse_args()

  if args.debug:
    # event_id, timestamp, product_id, user_id 
    users = defaultdict(lambda: defaultdict(list))
    f = [
      ['','product_detail_clicked','','2014-02-22T14:00:00.00001Z','','','','','','','','','1','','','','1337'],
      ['','product_detail_clicked','','2014-02-22T14:00:01.00001Z','','','','','','','','','2','','','','1337'],
      ['','product_detail_clicked','','2013-02-22T14:00:01.00001Z','','','','','','','','','12','','','','1338'],
    ]

    for l in f:
      utils.parse_eventline(l, users)
  else:
    users = utils.create_usermatrix(args.inputfile)
  usermatrix_to_file(users, args.outputfile, args.method)

if __name__ == '__main__':
  main()
