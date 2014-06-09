import pymongo
import os
import sys
from bson import Binary, Code
import helpers
import matplotlib.pyplot as plt
import numpy as np
import math
import longTailSomething

def main(sessDB='sessionsNew'):
    '''
    '''
    longTailSomething.main()
    thresholds = np.arange(0,1.0001,0.0001)
    threshold = .30
    countsOnItems = helpers.getKGroups('product_id',sessDB)
    print ()
    print ("Pareto's principle")
    print ('Threshold \t& Cut at \t& Account for ratings \\\\')
    bars = []
    percentages = []
    for t in thresholds:
        counts,items = getMostFrequentItems(countsOnItems,t)
        ratingsPercentage = findRatingsPercentage(counts,countsOnItems)
        bars.append(len(counts))
        percentages.append(ratingsPercentage)
        print ("%s \t& \t %s \t&\t %s \\\\" % (t*100, len(counts),ratingsPercentage))
        # print ("(%s, %s)" % (t*100, ratingsPercentage))
    # plotTwins(bars,percentages,thresholds)

def plotTwins(bars,percentages,thresholds):
    fig, ax1 = plt.subplots()
    width = 0.1

    ax1.plot(
        thresholds,
        percentages,
        'b-'
    )
    ax1.set_xlabel('time (s)')
    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel('exp', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.axis([0, 1, 0, max(bars)])

    ax2.bar(
        thresholds,
        bars,
        width
    )
    ax2.set_ylabel('sin', color='r')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')


    plt.show()

def getMostFrequentItemsOld(countsOnItems,threshold):
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

def getMostFrequentItems(countsOnItems,threshold):
    '''
    '''
    counts_sorted = sorted(countsOnItems, key=lambda k: k['count'],reverse=True)
    counts = [(int(x['count'])) for x in counts_sorted]
    items = [int(x['product_id']) for x in counts_sorted]

    cut = math.ceil(len(counts)*threshold)
    # print (counts[:cut])
    return (counts[:cut]),items

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
    counts = [(int(x['count'])) for x in countsOnItems]
    avgRC = sum(counts)/len(counts)
    return avgRC

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
