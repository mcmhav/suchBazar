#!/usr/bin/env python
from scipy.stats import gaussian_kde
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description = 'Blend ratings')
parser.add_argument('-d', dest='dest', default="distributions", help="Where should we put our distributions?")
parser.add_argument('-i', dest='infolder', default="ratings", help="Which folder should we plot from?")
parser.add_argument('-c', dest='curve', action='store_true', default=False, help="Plot the density function as well")
args = parser.parse_args()

# Some preferences
BASEPATH = os.path.dirname(os.path.realpath(__file__))

INFOLDER = args.infolder
# Check if infolder is absolute
if args.infolder[0] != '/':
  INFOLDER = "%s/%s" % (BASEPATH, args.infolder)

print "Starting plotting from folder %s" % (INFOLDER)

# Create output folder if not exists.
if not os.path.exists(args.dest):
  os.makedirs(args.dest)

# Get all files in input-folder
rfiles = []
for root, dirs, files in os.walk(INFOLDER):
  for f in files:
    if f.endswith(".txt"):
      rfiles.append({"fpath": os.path.join(root, f), "fname": f})

# Iterate through all files (and create a plot for each)
for f in rfiles:
  fh = open(f["fpath"], "r")

  # Initialize the x-array, empty.
  x = [0.0]*len(fh.readlines())
  fh.seek(0)

  # Parse CSV-file.
  i = 0
  ratings = []
  for row in csv.reader(fh, delimiter="\t"):
    user_id = int(row[0])
    product_id = int(row[1])
    rating = float(row[2])
    x[i] = rating
    ratings.append(rating)
    i += 1

  # Number of bars, should be pretty high to show granularity.
  num_bins = 150

  # the histogram of the data
  fig, ax = plt.subplots()
  n, bins, patches = ax.hist(x, num_bins, facecolor='green', normed=args.curve, alpha=0.5)

  # We manually set the x-lim.
  ax.set_xlim((0.9, 5.1))

  # Add best fit line
  if args.curve:
    density = gaussian_kde(x)

    # Set co-variance factor, lower means more detail.
    density.covariance_factor = lambda : .25
    density._compute_covariance()

    # Create linear space with 200 samples.
    xs = np.linspace(1,5,200)

    # Plot the density function.
    ax.plot(xs, density(xs), 'r--', linewidth=1)

  plt.xlabel('Rating')
  plt.ylabel('Number of ratings')

  plt.savefig("%s/%s.png" % (args.dest, f["fname"][:-4]))
  plt.clf()

print "Success. Plotted %d files into %s" % (len(rfiles), args.dest)
