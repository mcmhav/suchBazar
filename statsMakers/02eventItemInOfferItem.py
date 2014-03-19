import json
import pymongo
import csv
import argparse
import os
import sys

parser = argparse.ArgumentParser(description='Divides each store into 5 children events. Count children and visualize this distribution.')
parser.add_argument('-v',dest='v', action='store_true')
parser.add_argument('-sc',type=str, default="sessions")
parser.set_defaults(v=True)
parser.set_defaults(t=False)
args = parser.parse_args()

print ("Verbose:                     %d" % args.v)
print ("Sessions collection used:    %s" % args.sc)
print ("")

client = pymongo.MongoClient()
db = client.mydb
opCol = db['offerprod']
stCol = db['offerstaging']
stNCol = db['offerstaging1003']
prCol = db['prod']
seCol = db['sessions']
cleanCol = db['cleanedItems']

def main():
    handle_appStarted()

def handle_appStarted():
    ofItems = opCol.distinct('id')
    stItems = stCol.distinct('id')
    stNItems = stNCol.distinct('id')

    prItems = prCol.distinct('product_id')
    seItems = seCol.distinct('product_id')

    clItems = cleanCol.distinct('product_id')

    # nonMatching(ofItems,prItems)
    # nonMatching(stItems,prItems)
    # nonMatching(stNItems,prItems)

    # nonMatching(ofItems,seItems)
    # nonMatching(stItems,seItems)
    # nonMatching(stNItems,seItems)

    nonMatching(stItems,clItems)



def nonMatching(list1,list2):
    nonMatch = 0
    for item in list2:
        if str(item) not in list1:
            nonMatch += 1

    matchRatio = (nonMatch/len(list1))*100
    print ("NonMatching values is:          %s" % nonMatch)
    print ("List1 length:                   %s" % len(list1))
    print ("List2 length:                   %s" % len(list2))
    print ("Items from list2 not in list1:  %s" % matchRatio)
    print ("")

if __name__ == "__main__":
    main()
