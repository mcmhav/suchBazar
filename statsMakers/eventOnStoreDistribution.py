import json
import pymongo
import csv
import argparse
import os
import sys
from bson import Binary, Code
import helpers
import matplotlib.pyplot as plt
import numpy as np

def main(sessDB='sessionsNew'):
    groups = groupStoreEvents(sessDB)
    print groups

    sys.exit()

def groupStoreEvents(sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = col.group(
                           key={'storefront_name':1, 'event_id':1},
                           condition={},
                           reduce=reducer,
                           initial={'count':0}
                       )
    return groups

def makePlot(groups,k):
    '''
    '''
    ks = [str(x[k]) for x in groups]
    counts = [int(x['count']) for x in groups]
    if (k == 'storefront_name'):
        i = 0
        tmpCounts = counts[:]
        for count in counts:
            if (count < 200):
                del tmpCounts[i]
                del ks[i]
                i -= 1
            i += 1
        counts = tmpCounts[:]

    index = np.arange(len(counts))
    width = 0.8

    fig, ax = plt.subplots()
    fig.set_size_inches(14.0,8.0)
    plt.bar(index, counts, width)
    plt.title("Events id distribution")

    plt.xticks(index+width/2., ks)
    plt.ylabel('Event count')
    plt.xlabel('Event id')
    # ax.set_xticks(range(0,len(counts)+2))

    fig.autofmt_xdate()
    # ax.set_xticklabels(ks)

    plt.axis([0, len(ks), 0, max(counts) + (max(counts)/100)])
    plt.grid(True)
    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/" + k + "distribution.png"
    plt.savefig(location)
    plt.show()
    print ('Price distribution written to: %s' % location)
    N = 5
    menMeans   = (20, 35, 30, 35, 27)
    womenMeans = (25, 32, 34, 20, 25)
    menStd     = (2, 3, 4, 1, 2)
    womenStd   = (3, 5, 2, 3, 3)
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, menMeans,   width, color='r', yerr=womenStd)
    p2 = plt.bar(ind, womenMeans, width, color='y',
                 bottom=menMeans, yerr=menStd)

    plt.ylabel('Scores')
    plt.title('Scores by group and gender')
    plt.xticks(ind+width/2., ('G1', 'G2', 'G3', 'G4', 'G5') )
    plt.yticks(np.arange(0,81,10))
    plt.legend( (p1[0], p2[0]), ('Men', 'Women') )

    plt.show()


def getLabelFromItemDB(bids):
    labels = []
    col = helpers.getCollection('brandstaging')

    for bid in bids:
        for dbId in col.find():
            if (bid) == str(float(dbId['id'])):
                labels.append(dbId['displayName'])
    return labels

useVals = {
    "storefront_name",
}

if __name__ == "__main__":
    main()
