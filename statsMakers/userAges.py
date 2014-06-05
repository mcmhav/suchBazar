import datetime
import sys
import helpers
from bson import Binary, Code
import math
import numpy as np
import matplotlib.pyplot as plt
import os
from pylab import *

def main(sessDB='sessionsNew'):
    '''
    '''
    col = helpers.getCollection(sessDB)
    groups = getMaxMinForUsers(col)
    timeSpans = [int(x['timespan']) for x in groups]
    plotItemTimeSpans(timeSpans)
    doublePlotAVG(groups)

def doublePlotAVG(groups):
    '''
    '''
    counts = [int(x['count']) for x in groups]
    counts = cutTopN(counts,10)
    maxikus = max(counts) + 1
    tot = [0] * maxikus
    ccount = [0] * maxikus
    for g in groups:
        if not g['count'] > maxikus:
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
    ax1.set_xlabel('Event count of user')
    ax1.axis([0, len(y)+(len(y)/80), 0, max(y)+(max(y)/80)])

    plot(xr,yr, 'yo', xr, fit_fn(xr), '--k',color='r',markersize=0)

    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/avglifetimeoncountuser.png"
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

def cutTopN(listur,N):
    for i in range(0,N):
        listur.remove(max(listur))
    return listur

def plotItemTimeSpans(timeSpans):
    '''
    '''
    buckets,xTicks = makeBuckets(timeSpans)
    ks = np.arange(0,len(buckets))
    helpers.makePlot(
        'userTimespans',
        buckets,
        yaxis=ks,
        # title='Time between first event on item till the last',
        ylabel='Amount of users',
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

def getMaxMinForUsers(col):
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
    k = 'user_id'
    groups = col.group(
        key={k:1},
        condition={'$and':[
                    {k:{'$ne':'NULL'}},
                    {k:{'$ne':'N/A'}},
                    {k:{'$ne':''}},
                ]},
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
