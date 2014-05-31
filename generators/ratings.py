#!/usr/bin/env python
import argparse
from collections import defaultdict
import numpy as np
import sys
import utils
import os
from datetime import datetime

valid_methods = ['naive', 'recentness', 'count']
valid_functions = ['sigmoid_fixed', 'sigmoid_constant', 'linear', 'norm_dist']

def main():
  config = {}

  parser = argparse.ArgumentParser(description = 'Generate ratings file')
  parser.add_argument('-i', dest='inputfile', default='../data/sobazar.tab', help="Defaulting to data/proddata.tab")
  parser.add_argument('-o', dest='outputfile', help="Defaulting to '<method-name>.txt'")
  parser.add_argument('-d', dest='outputfolder', default='ratings', help="Defaulting to 'ratings'")
  parser.add_argument('-t', dest='timestamps', action='store_true', default=False, help="Include timestamps in output")
  parser.add_argument('-f', dest='force', action='store_true', default=False, help='Create rating file, even if it already exist')
  parser.add_argument('--debug', dest='debug', action='store_true', default=False)
  parser.add_argument('--skip-header', dest='skipheader', action='store_true', default=False)
  parser.add_argument('--min-date', dest='min_date', default=None)
  parser.add_argument('--max-date', dest='max_date', default=None)

  # Method and curve options.
  parser.add_argument('-m', dest='method', help="Choose which method to use")
  parser.add_argument('-fx', dest='fx', help="Choose which function type to use")
  parser.add_argument('-mx', dest='minmax', default="user", help="Calculate score based on user recentness or globally?")

  # Linear options
  parser.add_argument('-lg', dest='lg', help="Choose growth of linear function")

  # Normal dist options
  parser.add_argument('-sd', dest='sd', help="Standard deviation for using normal distribution")

  # Sigmoid options
  parser.add_argument('-sr', dest='sigmoid_ratio', help="Choose ratio between steepness and increase, for sigmoid")
  parser.add_argument('-sc', dest='sigmoid_constant', help="Choose X for steepest point in sigmoid")
  parser.add_argument('-sm', dest='sigmoid_constant_average', action='store_true', help="Select the sigmoid constant automatically by average")
  args = parser.parse_args()

  # Set method.
  if args.method:
    if args.method in valid_methods: config["method"] = args.method
  if not config.get("method", None):
    print ("Wrong method '%s', please choose between %s with '-m' flag" % (args.method, valid_methods))
    sys.exit(1)

  # Define how the curve will look.
  if args.fx:
    if args.fx in valid_functions: config["fx"] = args.fx
  if args.fx and 'naive' in args.method:
    print ("It does not make sense to define fx when using naive methods.")
    sys.exit(1)
  if not config.get("fx", None) and args.method != "naive":
    print ("Wrong function type '%s', please choose between %s with '-fx' flag" % (args.fx, valid_functions))
    sys.exit(1)

  # Set the sigmoid options, if the method is in use.
  if args.fx and 'sigmoid' in args.fx:
    if args.sigmoid_ratio: config["sigmoid_ratio"] = float(args.sigmoid_ratio)
    if args.sigmoid_constant: config["sigmoid_constant"] = float(args.sigmoid_constant)
    if args.sigmoid_constant_average: config["sigmoid_constant_average"] = True

    if "fixed" in config["fx"] and not config.get("sigmoid_ratio", None):
        print ("[WARN] Sigmoid ratio not set. Defaulting to 4. Set with -sr")
        config["sigmoid_ratio"] = 4
    if "constant" in config["fx"] and not config.get("sigmoid_constant", None) and not config.get("sigmoid_constant_average", None):
        print ("[WARN] Sigmoid constant not set. Defaulting to 30. Set with -sc or use average with -sm")
        config["sigmoid_constant"] = 30

  # Standard deviation options in normal distribution
  if args.fx and 'norm_dist' in args.fx:
    if args.sd: config["norm_standard_dev"] = float(args.sd)
    else:
      print ("[WARN] Standard deviation not set. Defaulting to 5.0")
      config["norm_standard_dev"] = 5

  # Guess filename if not provided.
  if not args.outputfile:
    params = ""
    if config.get("sigmoid_constant", None) or config.get("sigmoid_ratio", None):
      params = "_sc-" + str(config["sigmoid_constant"]) if config.get("sigmoid_constant", None) else "_sr-" + str(config["sigmoid_ratio"])
    if config.get("norm_standard_dev", None):
      params = "_sd-" + args.sd
    if config.get("sigmoid_constant_average"):
      params = "_sc-average"

    if args.fx:
      args.outputfile = config["method"] + "_" + config["fx"] + params + '.txt'
    else:
      args.outputfile = config["method"] + '.txt'
  base_dir = os.path.dirname(os.path.realpath(__file__))

  # Check if the outfolder is relative
  config["outfile"] = args.outputfolder
  if args.outputfolder[0] != '/':
    config["outfile"] = "%s/%s" % (base_dir, config["outfile"])

  # Ensure the folder exists.
  if not os.path.exists(config["outfile"]):
    os.makedirs(config["outfile"])

  # Make it absolute (add the filename to folder)
  config["outfile"] = "%s/%s" % (config["outfile"], args.outputfile)

  # Check if we want timestamps in output
  config["timestamps"] = args.timestamps

  # Which method to do minmax.
  config["minmax"] = args.minmax if args.minmax == 'user' else 'global'

  # Check if we want a minimum date
  if args.min_date:
    t = datetime.strptime(args.min_date, "%Y-%m-%d")
    config["min_date"] = t

  if args.max_date:
    t = datetime.strptime(args.max_date, "%Y-%m-%d")
    config["max_date"] = t

  # Check that the input file exists.
  if os.path.isfile(args.inputfile):
    config["infile"] = args.inputfile
  elif args.inputfile == 'mongo':
    config["infile"] = args.inputfile
  if not config.get("infile", None):
    print ("Could not find file: %s. Ensure you have provided correct file with -i option") % args.inputfile
    sys.exit(1)

  # Check if we want to skip first line in csv
  if args.skipheader:
    config["skipheader"] = args.skipheader

  # Check if we want force mode.
  if not args.force:
    # Check if the output file already exist.
    if os.path.isfile(config["outfile"]):
      print ("File '%s' already exists. Skipping. Enable force-mode with -f if you want to continue." % args.outputfile)
      sys.exit(0)

  # Give some useful info to the user.
  print ("----------------------------------------------------------------------")
  print ("Using following config to generate rankings to %s" % args.outputfile)
  for k, i in config.items():
    print ("%s => %s" % (k,i))
  print ("----------------------------------------------------------------------")

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
      utils.parse_eventline(l, users, config)
  else:
    users = utils.create_usermatrix(config)

  # Reset the file for output
  open(config["outfile"], 'w').close()

  # Then write our contents to the output file.
  ratings = []
  with open(config["outfile"], 'a') as output:
    for user_id, products in users.items():
      # Get rating for user_id and events connected to this user.
      r = utils.get_ratings_from_user(user_id, products, output, config)
      utils.write_ratings_to_file(user_id, r, output, config)
      ratings.extend([rat for product_id, rat in r.items()])
  print ("Success. Wrote %d ratings to %s. Average: %s, Median: %s, Min: %.2f, Max: %.2f" %
    (len(ratings), args.outputfile, np.mean(ratings), np.median(ratings), np.min(ratings), np.max(ratings)))

if __name__ == '__main__':
  main()
