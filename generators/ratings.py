#!/usr/bin/env python
import argparse
from collections import defaultdict
import numpy as np
import sys
import utils

def main():
  parser = argparse.ArgumentParser(description = 'Generate ratings file')
  parser.add_argument('-i', dest='inputfile', default='../data/sobazar.tab', help="Defaulting to data/proddata.tab")
  parser.add_argument('-o', type=str, dest='outputfile', default='ratings.txt', help="Defaulting to '<method-name>.txt'")
  parser.add_argument('-d', dest='outputfolder', default='ratings', help="Defaulting to 'ratings'")
  parser.add_argument('-m', dest='method', default='srecent', help="Choose between 'naive', 'scount' and 'srecent'")
  parser.add_argument('--debug', dest='debug', action='store_true', default=False)
  args = parser.parse_args()

  if args.method not in ['scount', 'srecent', 'naive']:
    print ("Wrong method '%s', please choose between 'scount', 'srecent' and 'naive'") % (args.method)
    sys.exit(1)

  if args.outputfile == '':
    args.outputfile = args.method + '.txt'
  args.outputfile = args.outputfolder + '/' + args.outputfile

  # print (get_data("data/proddata.tab"))
  print ("Using method %s in order to generate rankings to %s" % (args.method, args.outputfile))


  # print (get_data(proddata.tab))
  if args.debug:
    # event_id, timestamp, product_id, user_id
    users = defaultdict(lambda: defaultdict(list))
    f = [
      ['','product_purchased','','2014-02-22T14:00:00.00001Z','','','','','','','','','1','','','','1337'],
      ['','product_detail_clicked','','2014-02-22T14:00:01.00001Z','','','','','','','','','2','','','','1337'],
      ['','product_purchased','','2014-02-23T14:00:00.00001Z','','','','','','','','','3','','','','1337'],
      ['','product_purchased','','2014-02-22T14:00:02.00001Z','','','','','','','','','12','','','','1338'],
    ]

    for l in f:
      utils.parse_eventline(l, users)
  else:
    users = utils.create_usermatrix(args.inputfile)

  # Reset the file for output
  open(args.outputfile, 'w').close()

  # Then write our contents to the output file.
  ratings = []
  with open(args.outputfile, 'a') as output:
    for user_id, products in users.items():
      # Get rating for user_id and events connected to this user.
      r = utils.get_ratings_from_user(user_id, products, output, args.method)
      utils.write_ratings_to_file(user_id, r, output)
      ratings.extend([rat for product_id, rat in r.items()])
  print ("Success. Wrote %d ratings to %s. Average: %s, Median: %s" %
    (len(ratings), args.outputfile, np.mean(ratings), np.median(ratings)))

if __name__ == '__main__':
  main()
