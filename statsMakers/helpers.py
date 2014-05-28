import sys
import json
import pymongo
import csv
import os
import helpers
from bson import Binary, Code
import numpy as np
import matplotlib.pyplot as plt

f = ""

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
    print ('\r[{0}] {1}%'.format('#'*(progress/10), progress))

def makePlot(
                k,ks,counts,
                width=0.8,
                figsize=[14.0,8.0],
                title="tmp",
                ylabel='tmpylabel',
                xlabel='tmpxlabel',
                labels=[],
                show=False,
                grid=True,
                xticks=[],
                yticks=[]
            ):
    '''
    '''
    if not labels:
        labels = ks
    index = np.arange(len(ks))

    fig, ax = plt.subplots()
    fig.set_size_inches(figsize[0],figsize[1])
    plt.bar(index, counts, width)

    plt.title(title)
    if not xticks:
        print ('Making xticks')
        xticks.append(index+width/2.)
        xticks.append(labels)
        print ('Done making xticks')

    if yticks:
        print ('Making yticks')
        # plt.yticks([1,2000],[0,100])
        plt.yticks(yticks[0],yticks[1])
        # ax.set_yticks(np.arange(0,100,10))
        print ('Done making yticks')

    plt.xticks(xticks[0], xticks[1])
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    # ax.set_xticks(range(0,len(counts)+2))

    fig.autofmt_xdate()
    # ax.set_xticklabels(ks)

    plt.axis([0, len(ks), 0, max(counts) + (max(counts)/100)])
    plt.grid(grid)
    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/" + k + "distribution.png"
    plt.savefig(location)
    if show:
        plt.show()
    print ('Price distribution written to: %s' % location)

def getKGroups(k,sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

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

if __name__ == "__main__":
    main()

