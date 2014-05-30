import pymongo
import os
import sys
from bson import Binary, Code
import helpers
import matplotlib.pyplot as plt
import numpy as np
import math


def main(sessDB='sessionsNew'):
    '''
    '''
    countsOnItems = helpers.getKGroups('product_id',sessDB)
    avgRC,iut,cut = findItemsUnder50Treshhold(countsOnItems)
    coverage = findCoverage(iut,cut,len(countsOnItems))
    ratingsPercentage = findRatingsPercentage(cut,countsOnItems)
    print (len(countsOnItems))
    print (len(cut))
    print (avgRC)
    print (coverage)
    print (ratingsPercentage)

def findItemsUnder50Treshhold(countsOnItems):
    '''
    '''
    avgRC = findAverageRatingCount(countsOnItems)
    listsorted = sorted(countsOnItems, key=lambda k: k['count'])

    items = [int(x['product_id']) for x in listsorted]
    counts = [int(x['count']) for x in listsorted]

    i = 0
    for c in counts:
        if avgRC < c:
            break
        i += 1
    return avgRC,items[:i],counts[:i]

def findAverageRatingCount(countsOnItems):
    '''
    '''
    counts = [(int(x['count'])-1) for x in countsOnItems]
    avgRC = sum(counts)/len(counts)
    return avgRC

def findCoverage(iut,cut,total):
    '''
    '''
    return (len(cut)/total)*100

def findRatingsPercentage(cut,countsOnItems):
    '''
    '''
    counts = [int(x['count']) for x in countsOnItems]
    return (sum(cut)/sum(counts)*100)

if __name__ == "__main__":
    main()
