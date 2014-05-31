import datetime
import sys
import argparse
import helpers
from bson import Binary, Code
import math
import numpy as np
import matplotlib.pyplot as plt
import os

def main(sessDB='sessionsNew'):
    groups = makeGroups(sessDB)

    timeSpans = [int(x['timespan']) for x in groups]
    counts = [int(x['count']) for x in groups]
    # plotItemTimeSpans(timeSpans)
    plotItemTimeSpansSortedOnCount(groups)

def plotItemTimeSpansSortedOnCount(groups):
    '''
    '''
    groups_sorted = sorted(groups, key=lambda k: k['count'],reverse=True)
    timeSpans = [int(x['timespan']) for x in groups_sorted]
    counts = [int(x['count']) for x in groups_sorted]
    doublePlotLol(timeSpans,counts)

def doublePlotLol(timeSpans,counts):
    '''
    '''

    print(counts)
    fig, ax = plt.subplots()
    figsize=[14.0,8.0]
    fig.set_size_inches(figsize[0],figsize[1])
    width = 0.8
    index = np.arange(len(counts))
    # helpers.makePlot(
    #     'itemTimespans',
    #     ks,
    #     timeSpans,
    #     title='Time between first event on item till the last',
    #     ylabel='Amount of items',
    #     xlabel='Time in weeks',
    #     show=False,
    #     grid=False,
    #     xticks=makeCountsXticks(counts)
    # )
    ptt = plt.bar(index, timeSpans, width, color='b')
    ptc = plt.plot(index, counts, '|', color='b',markersize=4)

    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/itemTimeSpansortedoneventcount.png"
    plt.savefig(location)
    plt.show()
    print ('Distribution written to: %s' % location)

    # plt.plot(counts, 'bo', markersize=4)

    # plt.show()

def makeCountsXticks(counts):
    xticks = helpers.makeTicks(0,len(counts))
    xticksLabels = helpers.makeTicks(0,max(counts),-5)
    xTicks = []
    xTicks.append(xticks)
    xTicks.append(xticksLabels)
    return xTicks

def plotItemTimeSpans(timeSpans):
    '''
    '''
    buckets,xTicks = makeBuckets(timeSpans)
    ks = np.arange(0,len(buckets))
    helpers.makePlot(
        'itemTimespans',
        ks,
        buckets,
        # title='Time between first event on item till the last',
        ylabel='Amount of items',
        xlabel='Time in weeks',
        show=False,
        grid=True,
        xticks=xTicks
    )

def makeBuckets(timeSpans):
    '''
    '''
    time_sorted = sorted(timeSpans)
    maxTime = max(time_sorted)
    avg = sum(time_sorted)/len(time_sorted)
    bc = (math.ceil(maxTime/avg)*4)
    buckets = [0] * bc
    for ua in time_sorted:
        place = math.floor(ua/(avg/4))
        buckets[place] += 1

    xticks = helpers.makeTicks(0,bc,steps=20)
    xticksLabels = helpers.makeTicks(0,int(maxTime/(1000*60*60*24*7)),steps=20)
    xTicks = []
    xTicks.append(xticks)
    xTicks.append(xticksLabels)
    return buckets,xTicks

def makeCSVFiles(groups):
    maxTimespan = 0
    maxItem = ''
    greaterThan1 = 0

    c = helpers.getCSVWriter("itemEventCount")
    c.writerow([ 'product_id', 'count' ])

    cts = helpers.getCSVWriter("timespanStats")
    cts.writerow([ 'product_id', 'timespan' ])

    cNts = helpers.getCSVWriter("timespanWithCountStats")
    cNts.writerow([ 'product_id', 'timespan', 'count' ])

    for item in groups:
        if item['timespan'] > maxTimespan:
            maxTimespan = item['timespan']
            maxItem = item['product_id']
        print (item)
        if (item['count'] > 1):
            greaterThan1 += 1

        c.writerow([ 'p' + str(int(item['product_id'])), int(item['count'])])
        cts.writerow([ 'p' + str(int(item['product_id'])), int(item['timespan']/(1000*60))])
        cNts.writerow([ 'p' + str(int(item['product_id'])), int(item['timespan']/(1000*60)), int(item['count'])])
    helpers.closeF()

def makeObjectForJson(groups):
    e = open("piss" + '.json','w')
    e.write("[\n")
    for item in groups:
        start = datetime.datetime.fromtimestamp(int(item['min'])/1000).strftime('%m/%d/%Y')
        end = datetime.datetime.fromtimestamp((int(item['max'])/1000)+(60*60*24)).strftime('%m/%d/%Y')
        e.write("['" + str(item['product_id']) + "', " + "new Date('" + start + "'), " + "new Date('" + end + "')],\n")
    e.write("]")
    e.close()

def makeGroups(sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        if (cur.ts > result.max) {
                            result.max = cur.ts;
                        }
                        if (cur.ts < result.min) {
                            result.min = cur.ts;
                        }
                        result.count += 1;
                        result.timespan = result.max - result.min;
                        result.avgTime = result.timespan/result.count;
                    }
                   """)

    groups = col.group(
        key={'product_id':1},
        condition={'product_id':{'$ne':'NULL'}},
        reduce=reducer,
        initial={
            'count':0,
            'max':0,
            'min':13842573649850,
            'timespan':0,
            'avgTime':0
        }
    )
    return groups

if __name__ == "__main__":
    main()
