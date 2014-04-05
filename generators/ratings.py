#!/usr/bin/env python
import argparse

import utils

def usermatrix_to_file(users, filename):
  # Reset the file
  open(filename, 'w').close()

  # Then write our contents to the output file.
  with open(filename, 'a') as output:
    for user_id, products in users.iteritems():
      utils.products_to_file(user_id, products, output)

def main():
  parser = argparse.ArgumentParser(description = 'Generate ratings file')
  parser.add_argument('inputfile')
  parser.add_argument('-o', dest='outputfile', default='output.csv')
  args = parser.parse_args()

  users = utils.create_usermatrix(args.inputfile)
  usermatrix_to_file(users, args.outputfile)

if __name__ == '__main__':
  main()
