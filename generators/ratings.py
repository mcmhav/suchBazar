#!/usr/bin/env python
import argparse
from collections import defaultdict
import numpy as np
import sys
import utils
import os

valid_methods = ['naive', 'recentness', 'count']
valid_functions = ['sigmoid_fixed', 'sigmoid_constant', 'linear']

def main():
  config = {}

  parser = argparse.ArgumentParser(description = 'Generate ratings file')
  parser.add_argument('-i', dest='inputfile', default='../data/sobazar.tab', help="Defaulting to data/proddata.tab")
  parser.add_argument('-o', dest='outputfile', help="Defaulting to '<method-name>.txt'")
  parser.add_argument('-d', dest='outputfolder', default='ratings', help="Defaulting to 'ratings'")
  parser.add_argument('--debug', dest='debug', action='store_true', default=False)
  parser.add_argument('--skip-header', dest='skipheader', action='store_true', default=False)

  # Method and curve options.
  parser.add_argument('-m', dest='method', help="Choose which method to use")
  parser.add_argument('-fx', dest='fx', help="Choose which function type to use")

  # Linear options
  parser.add_argument('-lg', dest='lg', help="Choose growth of linear function")

  # Sigmoid options
  parser.add_argument('-sr', dest='sigmoid_ratio', help="Choose ratio between steepness and increase, for sigmoid")
  parser.add_argument('-sc', dest='sigmoid_constant', help="Choose X for steepest point in sigmoid")
  args = parser.parse_args()

  # Set method.
  if args.method:
    if args.method in valid_methods: config["method"] = args.method
  if not config.get("method", None):
    print ("Wrong method '%s', please choose between %s with '-m' flag") % (args.method, valid_methods)
    sys.exit(1)

  # Define how the curve will look.
  if args.fx:
    if args.fx in valid_functions: config["fx"] = args.fx
  if args.fx and 'naive' in args.method:
    print "It does not make sense to define fx when using naive methods."
    sys.exit(1)
  if not config.get("fx", None):
    print "Wrong function type '%s', please choose between %s with '-fx' flag" % (args.fx, valid_functions)
    sys.exit(1)

  # Set the sigmoid options, if the method is in use.
  if 'sigmoid' in args.fx:
    if args.sigmoid_ratio: config["sigmoid_ratio"] = float(args.sigmoid_ratio)
    if args.sigmoid_constant: config["sigmoid_constant"] = float(args.sigmoid_constant)
    if "fixed" in config["fx"] and not config.get("sigmoid_ratio", None):
        print "[WARN] Sigmoid ratio not set. Defaulting to 4. Set with -sr"
        config["sigmoid_ratio"] = 4
    if "constant" in config["fx"] and not config.get("sigmoid_constant", None):
        print "[WARN] Sigmoid constant not set. Defaulting to 30. Set with -sc"
        config["sigmoid_constant"] = 30

  # Guess filename if not provided.
  if not args.outputfile:
    params = ""
    if config.get("sigmoid_constant", None) or config.get("sigmoid_ratio", None):
      params = "sc-" + str(config["sigmoid_constant"]) if config.get("sigmoid_constant", None) else "sr-" + str(config["sigmoid_ratio"])
    args.outputfile = config["method"] + "_" + config["fx"] + "_" + params + '.txt'
  config["outfile"] = args.outputfolder + '/' + args.outputfile

  # Check that the input file exists.
  if os.path.isfile(args.inputfile):
    config["infile"] = args.inputfile
  if not config.get("infile", None):
    print "Could not find file: %s. Ensure you have provided correct file with -i option" % args.inputfile
    sys.exit(1)

  # Check if we want to skip first line in csv
  if args.skipheader:
    config["skipheader"] = args.skipheader

  # Give some useful info to the user.
  print "----------------------------------------------------------------------"
  print "Using following config to generate rankings to %s" % (args.outputfile)
  for k, i in config.iteritems():
    print "%s => %s" % (k,i)
  print "----------------------------------------------------------------------"

  # print (get_data(proddata.tab))
  if args.debug:
    # event_id, timestamp, product_id, user_id
    users = defaultdict(lambda: defaultdict(list))
    f = [
      ['','product_purchased','','2014-02-22T14:00:00.00001Z','','','','','','','','','1','','','','1337'],
      ['','product_detail_clicked','','2014-02-22T14:00:01.00001Z','','','','','','','','','2','','','','1337'],
      ['','product_purchased','','2014-02-23T14:00:00.00001Z','','','','','','','','','3','','','','1337'],

      ['','product_purchased','','2014-02-22T14:00:02.00001Z','','','','','','','','','12','','','','1338'],
      ['','product_purchased','','2014-02-22T14:00:03.00001Z','','','','','','','','','13','','','','1338'],

      ['','product_purchased','','2014-02-22T14:00:03.00001Z','','','','','','','','','12','','','','1339'],
    ]

    # Clean up the above input.
    for l in f:
      utils.parse_eventline(l, users)
  else:
    users = utils.create_usermatrix(config)

  # Reset the file for output
  open(config["outfile"], 'w').close()

  # Then write our contents to the output file.
  ratings = []
  with open(config["outfile"], 'a') as output:
    for user_id, products in users.iteritems():
      # Get rating for user_id and events connected to this user.
      r = utils.get_ratings_from_user(user_id, products, output, config)
      utils.write_ratings_to_file(user_id, r, output)
      ratings.extend([rat for product_id, rat in r.items()])
  print ("Success. Wrote %d ratings to %s. Average: %s, Median: %s, Min: %.2f, Max: %.2f" %
    (len(ratings), args.outputfile, np.mean(ratings), np.median(ratings), np.min(ratings), np.max(ratings)))

if __name__ == '__main__':
  main()
