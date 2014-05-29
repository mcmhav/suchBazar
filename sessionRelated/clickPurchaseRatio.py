#!/usr/bin/env python
from collections import defaultdict
import argparse
import os

def is_valid(inputs):
  for inp in inputs:
    if not inp or inp in ('N/A', '-1', 'NULL', 'null', 'testimplementation'):
      return False
  return True

def parse_eventline(line):
  row = line.split("\t")
  event_id = row[1]
  product_id = row[12]
  user_id = row[16]
  if is_valid([event_id, product_id, user_id]):
    return {"product_id": product_id, "event_id": event_id, "user_id": user_id}

def read_events(filename):
  # Dictionary holding users. All users has a dictionary with products.
  users = defaultdict(lambda: defaultdict(list))

  f = open(filename, "r")
  for line in f.readlines():
    event = parse_eventline(line)
    if event:
      u = event["user_id"]
      p = event["product_id"]
      users[u][p].append(event)
  return users

def get_abs_path(path):
  if path[0] != '/':
    abs_path = os.path.dirname(os.path.realpath(__file__))
    path = abs_path + '/' + path
  return path

def get_num_clicks_and_buys(events):
  # Returns the number of clicks and buys, found in a list of events.
  clicks = 0
  buys = 0
  for event in events:
    if event["event_id"] == "product_detail_clicked":
      clicks += 1
    elif event["event_id"] == "product_purchase_intended":
      buys += 1
  return clicks, buys

def get_user_ratio(num, products):
  clicks_at_n = 0
  buys_at_n = 0
  for pid, events in products.iteritems():
    # Get number of clicks and buys on this item.
    clicks, buys = get_num_clicks_and_buys(events)

    # If the number of clicks equals what we are looking for, then check if it is also bought.
    # Increment counters.
    if clicks == num:
      clicks_at_n += 1
      if buys > 0:
        buys_at_n += 1

  return float(clicks_at_n), float(buys_at_n)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = 'Get ratio between purchases and clicks')
  parser.add_argument('-i', dest='infile', help="Input file with events from session log", required=True)
  args = parser.parse_args()

  # Get absolute path
  args.infile = get_abs_path(args.infile)

  # Read events into an user dictionary, holding all products the user has
  # interacted with, furher categorized by events on that product.
  users = read_events(args.infile)

  # Iterate through the product ids.
  for i in range(1,10):
    tot_clicks = 0.0
    tot_buys = 0.0
    for uid, u_products in users.iteritems():
      clicks, buys = get_user_ratio(i, u_products)
      tot_clicks += clicks
      tot_buys += buys
    print "%d\t& %d\t& %d\t& %.2f \\\\" % (i, int(tot_clicks), int(tot_buys), tot_buys/tot_clicks)
