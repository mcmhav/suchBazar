#!/usr/bin/env python
import os
import csv
import matplotlib.pyplot as plt

# Some preferences
BASEPATH = os.path.dirname(os.path.realpath(__file__))
INFOLDER = "ratings"
OUTFOLDER = "dists"

print "Starting plotting from folder %s/%s" % (BASEPATH, INFOLDER)

# Create output folder if not exists.
if not os.path.exists(OUTFOLDER):
  os.makedirs(OUTFOLDER)

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
  for row in csv.reader(fh, delimiter="\t"):
    user_id = int(row[0])
    product_id = int(row[1])
    rating = float(row[2])
    x[i] = rating
    i += 1

  # Number of bars, should be pretty high to show granularity.
  num_bins = 150

  # the histogram of the data
  n, bins, patches = plt.hist(x, num_bins, range=(1.0, 5.0), normed=False, facecolor='green', alpha=0.5)

  plt.xlabel('Rating')
  plt.ylabel('Number of ratings')
  plt.title(f["fname"][:-4])

  plt.savefig("%s/%s/%s.png" % (BASEPATH, OUTFOLDER, f["fname"][:-4]))
  plt.clf()

print "Success. Plotted %d files into %s/%s" % (len(rfiles), BASEPATH, OUTFOLDER)
