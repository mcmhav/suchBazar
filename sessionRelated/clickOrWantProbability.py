#!/usr/bin/env python
from utils import read_events
import argparse

def num_events(events, patterns):
  count = [0]*len(patterns)
  for event in events:
    for i in range(len(patterns)):
      if event["event_id"] == patterns[i]:
        count[i] += 1
  return count

def all_exists(nums):
  for n in nums:
    if n < 1: return False
  return True

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description = 'Get ratio between purchases and clicks')
  parser.add_argument('-i', dest='infile', help="Input file with events from session log", required=True)
  args = parser.parse_args()

  users = read_events(args.infile)

  tot_events = 0.0
  tot_products = 0.0

  count_click_purchase = 0
  count_click_purchase_not_wanted = 0
  count_want_purchase = 0

  count_wanted = 0
  count_click = 0
  count_purchase = 0

  for uid, products in users.iteritems():
    for pid, events in products.iteritems():

      wanted = num_events(events, ['product_wanted'])
      if wanted[0] > 0:
        count_wanted += wanted[0]

      n = num_events(events, ['product_purchase_intended'])
      if n[0] > 0:
        count_purchase += n[0]

      n =  num_events(events, ['product_detail_clicked'])
      if n[0] > 0:
        count_click += n[0]

      n = num_events(events, ['product_detail_clicked', 'product_purchase_intended'])
      # Clicked & Purchase, where product is not Wanted.
      if all_exists(n):
        count_click_purchase += 1
        if wanted[0] == 0:
          count_click_purchase_not_wanted += 1

      n = num_events(events, ['product_wanted', 'product_purchase_intended'])
      if all_exists(n):
        count_want_purchase += 1

      tot_events += len(events)
      tot_products += 1

  p_click = count_click / tot_events
  p_want = count_wanted / tot_events
  p_purchase = count_purchase / tot_events

  p_click_and_purchase_not_wanted = count_click_purchase_not_wanted / tot_products
  p_click_and_purchase = count_click_purchase / tot_products
  p_want_and_purchase = count_want_purchase / tot_products

  p_purchase_given_want = p_want_and_purchase / p_want
  p_purchase_given_click = p_click_and_purchase / p_click
  p_purchase_given_click_not_wanted = p_click_and_purchase_not_wanted / p_click

  print "P(Click) = %.2f%%" % (p_click * 100)
  print "P(Want) = %.2f%%" % (p_want* 100)
  print "P(Purchase) = %.2f%%" % (p_purchase* 100)

  print "P(Purchase | Want) = %.2f%%" % (p_purchase_given_want * 100)
  print "P(Purchase | Click) = %.2f%%" % (p_purchase_given_click * 100)
  print "P(Purchase | (Click & !Wanted)) = %.2f%%" % (p_purchase_given_click_not_wanted * 100)
