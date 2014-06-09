import pymongo
import os
import sys
from bson import Binary, Code
import helpers
import matplotlib.pyplot as plt
import numpy as np
import math


def main(sessDB='sessionsNew3'):
    '''
    '''
    col = helpers.getCollection(sessDB)
    countsOnItems = helpers.getKGroups('product_id',sessDB)
    avgRC,iut,cut = findItemsUnder50Treshhold(countsOnItems,col)
    # print (cut)
    coverage = findCoverage(iut,cut,len(countsOnItems))
    ratingsPercentage = findRatingsPercentage(cut,countsOnItems)
    # print (len(countsOnItems))

    print ('Average count of ratings: %s' % avgRC)
    print ('Coverage: %s' % coverage)
    print ('Account for ratings: %s' % ratingsPercentage)
    print ()
    print ('Long tail')
    print ('Threshold \t& Cut  \t& Account for ratings \\\\')
    print ("- \t& \t %s \t&\t %s \\\\" % (len(cut),ratingsPercentage))

    # 6027
    # 4194
    # 6.594159615065538
    # 69.58685913389746
    # 28.540875122663113
    # [Finished in 1.3s]

def findItemsUnder50Treshhold(countsOnItems,col):
    '''
    '''
    avgRC = findAverageRatingCount(countsOnItems,col)
    listsorted = sorted(countsOnItems, key=lambda k: k['count'])

    items = [str(x['product_id']) for x in listsorted]
    counts = [int(x['count']) for x in listsorted]

    i = 0
    for c in counts:
        if avgRC < c:
            break
        i += 1

    print (i)

    return avgRC,items[:i],counts[:i]

def findAverageRatingCount(countsOnItems,col):
    '''
    '''
    products = len(col.distinct('product_id'))
    clicks = col.find({'event_id':'product_detail_clicked'}).count()
    wants = col.find({'event_id':'product_wanted'}).count()
    purchases = col.find({'event_id':'product_purchase_intended'}).count()
    totNumberOfItemInts = clicks + wants + purchases
    avgUIPI = totNumberOfItemInts/products

    # totNumberOfItemInts = clicks + wants + purchases

    # counts = [(int(x['count'])) for x in countsOnItems]
    # avgRC = sum(counts)/len(counts)
    return avgUIPI

def findCoverage(iut,cut,total):
    '''
    '''
    return (len(cut)/total)*100

def findRatingsPercentage(cut,countsOnItems):
    '''
    '''
    counts = [(int(x['count'])) for x in countsOnItems]
    return (sum(cut)/sum(counts)*100)

if __name__ == "__main__":
    main()
