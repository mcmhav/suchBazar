#!/usr/bin/env python
import argparse
from collections import defaultdict
import numpy as np
import sys

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
  print "Success. Wrote %d ratings to %s. Average: %s, Median: %s" % (len(ratings), filename, np.mean(ratings), np.median(ratings))

def main():
  parser = argparse.ArgumentParser(description = 'Generate ratings file')
  parser.add_argument('inputfile')
  parser.add_argument('-o', dest='outputfile', default='', help="Defaulting to '<method-name>.txt'")
  parser.add_argument('-d', dest='outputfolder', default='ratings', help="Defaulting to 'ratings'")
  parser.add_argument('-m', dest='method', default='naive', help="Choose between 'naive', 'scount' and 'srecent'")
  parser.add_argument('--debug', dest='debug', action='store_true', default=False)
  args = parser.parse_args()

  if args.method not in ['scount', 'srecent', 'naive']:
    print "Wrong method '%s', please choose between 'scount', 'srecent' and 'naive'" % (args.method)
    sys.exit(1)

  if args.outputfile == '':
    args.outputfile = args.method + '.txt'
  args.outputfile = args.outputfolder + '/' + args.outputfile

  print "Using method '%s' in order to generate rankings to '%s'" % (args.method, args.outputfile)

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
