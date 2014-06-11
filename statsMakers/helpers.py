import sys
import json
import pymongo
import csv
import os
import helpers
from bson import Binary, Code
import numpy as np
import matplotlib.pyplot as plt
import math

f = ""

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)

def main():
    '''
    Helper functions
    '''

def printProgress(count,total):
    progress = (count/total)*100
    sys.stdout.write("Progress: %s%%\r" % progress)
    sys.stdout.flush()

def is_json(myjson):
    try:
        json.loads(myjson)
    except (ValueError):
        return False
    return True

def getCollection(name,clean=False):
    client = pymongo.MongoClient()
    db = client.mydb
    col = db[name]
    if clean:
        col.remove()
    return col

def getCSVWriter(cFile):
    global f
    if sys.version_info >= (3,0,0):
        f = open(cFile + '.csv', "w", newline='')
    else:
        f = open(cFile + '.csv', "wb")
    return csv.writer(f)

def closeF():
    global f
    f.close()

def update_progress(count,total):
    print ('\r[{0}] {1}%'.format('#'*(count), total))

def makePlot(
                k,
                counts,
                yaxis=[],
                width=0.8,
                figsize=[14.0,8.0],
                title="",
                ylabel='tmpylabel',
                xlabel='tmpxlabel',
                labels=[],
                show=False,
                grid=True,
                xticks=[],
                yticks=[],
                steps=5,
                save=False
            ):
    '''
    '''
    if not list(yaxis):
        yaxis = np.arange(len(counts))
    if not labels:
        labels = yaxis
    index = np.arange(len(yaxis))

    fig, ax = plt.subplots()
    fig.set_size_inches(figsize[0],figsize[1])
    plt.bar(index, counts, width)

    plt.title(title)
    if not xticks:
        print ('Making xticks')
        ticks = makeTicks(yMax=len(yaxis),steps=steps)
        xticks.append(ticks+width/2.)
        xticks.append(labels)
        print ('Done making xticks')

    if yticks:
        print ('Making yticks')
        # plt.yticks([1,2000],[0,100])
        plt.yticks(yticks[0],yticks[1])
        # ax.set_yticks(np.arange(0,100,10))
        print ('Done making yticks')

    plt.xticks(xticks[0]+width/2., xticks[1])
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    # ax.set_xticks(range(0,len(counts)+2))

    fig.autofmt_xdate()
    # ax.set_xticklabels(ks)

    plt.axis([0, len(yaxis), 0, max(counts) + (max(counts)/100)])
    plt.grid(grid)
    location = ROOT_FOLDER + "/../muchBazar/src/image/" + k + "distribution.png"
    if save:
        plt.savefig(location)
        print ('Distribution written to: %s' % location)
    if show:
        plt.show()

def makeTicks(yMin=0,yMax=100,steps=5):
    '''
    '''
    stepSize = math.ceil(yMax/steps)
    index = np.arange(yMin,yMax+stepSize,stepSize)
    return index

def getKGroups(k,sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = col.group(
                           key={k:1},
                           condition={
                           '$and':[
                                {k:{'$ne':'NULL'}},
                                {k:{'$ne':'N/A'}},
                                {k:{'$ne':''}},
                            ]
                            },
                           reduce=reducer,
                           initial={'count':0}
                       )
    return groups


def getKGroupsWithEventIdDistr(ks,k,sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1;
                        tmp = result.storeCount;
                        currentEventId = cur.storefront_name;
                        hasProp = (tmp.hasOwnProperty(currentEventId));
                        if (hasProp) {
                            result.storeCount[cur.storefront_name] += 1;
                        }
                    }
                   """)
    groups = col.group(
        key={'event_id':1},
        condition={'$and':[
            {k:{'$ne':'NULL'}},
            {k:{'$ne':'N/A'}},
            {k:{'$ne':''}},
        ]},
        reduce=reducer,
        initial={
            'count':0,
            'storeCount':ks
        }
    )
    return groups

def plotAverageSomething(
        avgs,
        action,
        title='',
        ylabel='tmplabel',
        xlabel='tmplabel',
        show=False,
        grid=True,
        steps=10,
        labelTime=1000,
        capAtEnd=False,
        bucTuner=4,
        capVal=0,
        addCapped=False,
        save=False
    ):
    '''
    '''
    if capAtEnd:
        avgs = capIt(avgs,capVal,addCapped)

    buckets,xTicks = makeBuckets(avgs,steps=steps,labelTime=labelTime,bucTuner=bucTuner)
    print (buckets)
    print (xTicks)
    ks = np.arange(0,len(buckets))
    helpers.makePlot(
        action,
        buckets,
        yaxis=ks,
        title=title,
        ylabel=ylabel,
        xlabel=xlabel,
        show=show,
        grid=grid,
        xticks=xTicks,
        save=save
    )

def capIt(avgs,capVal,addCapped=False):
    avgs_sorted = sorted(avgs)
    underC,overC = findCountOverAndUnderAVG(avgs)
    testur = 1 - overC/underC
    tmps = int((len(avgs)-capVal))
    tmp = avgs_sorted[:tmps]
    if addCapped:
        for x in range(0,capVal):
            tmp.append(tmp[tmps-1])
    return tmp

def findCountOverAndUnderAVG(avgs):
    avg = sum(avgs)/len(avgs)
    underC = 0
    overC = 0
    for ua in avgs:
        if ua < avg:
            underC += 1
        else:
            overC += 1
    return underC,overC

def makeBuckets(avgs,bucTuner=4,steps=20,labelTime=1000):
    '''
    '''
    maxTime = max(avgs)
    avg = sum(avgs)/len(avgs)
    bc = (math.ceil(maxTime/avg)*bucTuner)
    buckets = [0] * bc
    for ua in avgs:
        place = math.floor(ua/(avg/bucTuner))
        buckets[place] += 1

    xticks = helpers.makeTicks(0,bc,steps=steps)
    xticksLabels = helpers.makeTicks(0,int(maxTime/labelTime),steps=steps)
    xTicks = []
    xTicks.append(xticks)
    xTicks.append(xticksLabels)
    buckets = removeTrailing0Buckets(buckets)
    return buckets,xTicks

def removeTrailing0Buckets(buckets):
    if buckets[-1]==0:
        buckets = removeTrailing0Buckets(buckets[:len(buckets)-1])
    return buckets


def getAvgOfCount(counts):
    return sum(counts)/len(counts)

def getUserEventOnItemCounts(sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        tmp = [
                            'product_purchase_intended',
                            'product_wanted',
                            'product_detail_clicked'
                        ];
                        hasProp = (tmp.indexOf(cur.event_id) > -1);
                        if (hasProp) {
                            result.count += 1
                        }
                    }
                   """)
    k = 'user_id'
    groups = col.group(
                           key={k:1},
                           condition={'$and':[
                                {k:{'$ne':'NULL'}},
                                {k:{'$ne':'N/A'}},
                                {k:{'$ne':''}}
                            ]},
                           reduce=reducer,
                           initial={'count':0}
                       )
    return groups

# def getUserAVGPrice(sessDB):
#     col = helpers.getCollection(sessDB)
#     reducer = Code("""
#                     function (cur,result) {
#                         cur.price
#                         tmp = [
#                             'product_purchase_intended',
#                             'product_wanted',
#                             'product_detail_clicked'
#                         ];
#                         hasProp = (tmp.indexOf(cur.event_id) > -1);
#                         if (hasProp) {
#                             result.count += 1
#                         }
#                     }
#                    """)
#     k = 'user_id'
#     groups = col.group(
#                            key={k:1},
#                            condition={'$and':[
#                                 {k:{'$ne':'NULL'}},
#                                 {k:{'$ne':'N/A'}},
#                                 {k:{'$ne':''}}
#                             ]},
#                            reduce=reducer,
#                            initial={'count':0}
#                        )
#     return groups

def getUserAVGPrice(sessDB):
    col = helpers.getCollection(sessDB)
    mapper = Code(  """
                    function () {
                        if (this.price != 'NULL' && this.price > 0){
                            emit(this.user_id, this.price);
                        }
                    }
                    """)

    reducer = Code( """
                    function (key, values) {
                        var total = 0;
                        for (var i = 0; i < values.length; i++) {
                            total += values[i];
                        }
                        avg = total/values.length;
                        return avg;
                    }
                    """)
    result = col.map_reduce(mapper, reducer, "myresults")
    return result.find()

if __name__ == "__main__":
    main()

