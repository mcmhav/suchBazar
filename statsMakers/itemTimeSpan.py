import datetime
import sys
import argparse
import helpers
from bson import Binary, Code
import math
import numpy as np
import matplotlib.pyplot as plt
import os
from pylab import *



def main(sessDB='sessionsNew'):
    groups = makeGroups(sessDB)

    timeSpans = [int(x['timespan']) for x in groups]
    counts = [int(x['count']) for x in groups]
    # plotItemTimeSpans(timeSpans)
    plotItemTimeSpansSortedOnCount(groups)

def plotItemTimeSpansSortedOnCount(groups):
    '''
    '''
    # doublePlotLol(groups)
    doublePlotAVG(groups)
    # plotAVGforCOuntAtleast(groups)

def plotAVGforCOuntAtleast(groups):
    '''
    '''
    groups = sorted(groups, key=lambda k: k['count'],reverse=False)
    counts = [int(x['count']) for x in groups]
    maxikus = max(counts) + 1
    tot = [0] * maxikus
    ccount = [0] * maxikus


    for g in groups:
        tmp = int(g['count'])
        tot[tmp] += (g['max'] - g['min'])
        ccount[tmp] += 1

    # print (tot)
    # print (ccount)
    bars = [0] * (maxikus + 1)
    c = 1
    itemS = 0
    tc = 0
    for x in range(1,maxikus+1):
        # print ("tot: %s\t bars: %s\t count: %s" % (tot[x-1],bars[x-1],c))
        if tot[x-1] != 0:
            itemS += ccount[x-2]
            tc += tot[x-1]
            tmp = tc/c
            bars[x] = tmp
            c += 1
        else:
            bars[x] = bars[x-1]


    # sys.exit()
    print (bars)

    x = range(0,len(bars))
    y = bars[::-1]

    helpers.makePlot(
        'avglifetimeoncountSUM',
        bars,
        # xticks=[helpers.makeTicks(yMax=len(bars)),list(helpers.makeTicks(yMax=maxikus))[::-1]],
        ylabel='Average lifetime in weeks',
        xlabel='Count of event',
        show=True
    )


def doublePlotAVG(groups):
    '''
    '''
    counts = [int(x['count']) for x in groups]
    maxikus = max(counts) + 1
    tot = [0] * maxikus
    ccount = [0] * maxikus
    for g in groups:
        tmp = int(g['count'])
        tot[tmp] += (g['max'] - g['min'])
        ccount[tmp] += 1

    bars = []
    reBars = []
    xr = []
    for x in range(0,maxikus):
        if ccount[x] != 0:
            tmp = (tot[x]/ccount[x])/(1000*60*60*24*7)
            bars.append(tmp)
            reBars.append(tmp)
            xr.append(x)
        else:
            bars.append(0)

    x = range(0,len(bars))
    y = bars

    yr = reBars
    xr = xr

    fit = polyfit(xr,yr,1)
    # fit_fn is now a function which takes in x and returns an estimate for y
    fit_fn = poly1d(fit)

    fig, ax1 = plt.subplots()
    figsize=[14.0,8.0]
    fig.set_size_inches(figsize[0],figsize[1])
    width = 0.8

    ax1.bar(x, y, width)
    ax1.set_ylabel('Average lifetime in weeks')
    ax1.set_xlabel('Event count on item')
    ax1.axis([0, len(y), 0, max(y)])

    plot(xr,yr, 'yo', xr, fit_fn(xr), '--k',color='r',markersize=0)

    plt.show()
    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/itemTimeSpansortedoneventcount.png"
    plt.savefig(location)
    print ('Distribution written to: %s' % location)


    # helpers.makePlot(
    #     'avglifetimeoncount',
    #     bars[::-1],
    #     xticks=[helpers.makeTicks(yMax=len(bars)),list(helpers.makeTicks(yMax=maxikus))[::-1]],
    #     ylabel='Average lifetime in weeks',
    #     xlabel='Count of event',
    #     show=True
    # )


def doublePlotLol(groups):
    '''
    '''
    groups_sorted = sorted(groups, key=lambda k: k['timespan'],reverse=True)
    groups_sorted = sorted(groups_sorted, key=lambda k: k['count'],reverse=True)
    timeSpans = [int(x['timespan']) for x in groups_sorted]
    counts = [int(x['count']) for x in groups_sorted]

    cap = 4724
    timeSpans = timeSpans[:cap]
    counts = counts[:cap]
    timeSpans = [x/(1000*60*60*24*7) for x in timeSpans]
    fig, ax1 = plt.subplots()
    figsize=[14.0,8.0]
    fig.set_size_inches(figsize[0],figsize[1])
    width = 0.8
    index = np.arange(len(counts))

    ax1.bar(index, timeSpans, width)
    ax1.set_ylabel('Timespan of item in weeks')
    ax1.axis([0, len(timeSpans), 0, max(timeSpans)])

    ax2 = ax1.twinx()
    ax2.set_ylabel('Event count on items', color='b')
    ax2.plot(index, counts, '|', color='b',markersize=4)
    ax2.axis([0, len(counts), 0, max(counts)])
    for tl in ax2.get_yticklabels():
            tl.set_color('b')

    plt.xticks([])

    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/itemTimeSpansortedoneventcount.png"
    plt.savefig(location)
    print ('Distribution written to: %s' % location)

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
        buckets,
        yaxis=ks,
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
        condition={
            'product_id':{'$ne':'NULL'},
            'ts': { '$gt': 1383283951000 }
        },
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
