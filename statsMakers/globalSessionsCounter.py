import csv
import argparse
import sys
import helpers
import matplotlib.pyplot as plt
import os
from bson import Binary, Code
import numpy as np

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)
DATA_FOLDER = 'data'
folder = SCRIPT_FOLDER + '/' + DATA_FOLDER

if not os.path.exists(folder):
        os.makedirs(folder)

filename = 'sessionxyNticks.csv'

def main(sessDB='sessionsNew'):
    if os.path.isfile(folder + '/' + filename):
        xaxis,yaxis,xticks = getFromFile(filename)
    else:
        xaxis,yaxis,xticks = handle_appStarted(sessDB)
        writeToFile(xaxis,yaxis,xticks,filename)

    print (xaxis)
    print (yaxis)
    helpers.makePlot(
        'sessionsCount',
        xaxis,
        yaxis=yaxis,
        # title='Global Sessions Count',
        ylabel='Amount of Users',
        xlabel='Session count',
        show=False,
        grid=True,
        xticks=[helpers.makeTicks(yMax=len(xaxis)),helpers.makeTicks(yMax=len(xaxis))]
    )

def getFromFile(filename):
    e = open(folder + "/" + filename,'r')
    line = e.readlines()
    e.close()
    xaxis = []
    yaxis = []
    ticks = []
    for ua in line[0].split(','):
        try:
            xaxis.append(int(ua))
        except:
            print ('lol')
    for ua in line[1].split(','):
        try:
            yaxis.append(int(ua))
        except:
            print ('lol')
    for ua in line[1].split(','):
        try:
            ticks.append(int(ua))
        except:
            print ('lol')

    return xaxis,yaxis,ticks

def writeToFile(xaxis,yaxis,xticks,name):
    e = open(folder + '/' + filename,'w')
    for x in xaxis:
        e.write(str(x) + ", ")
    e.write("\n")
    for y in yaxis:
        e.write(str(y) + ", ")
    e.write("\n")
    for t in xticks:
        e.write(str(t) + ", ")
    e.close()

def handle_appStarted(sessDB):
    col = helpers.getCollection(sessDB)
    userCount = -1
    sessionCount = 0
    prevSessionCount = 0
    preUserCount = 0
    sessionCounts = []
    userCounts = []
    # sessionCounts.append(0)
    userCounts.append(0)
    while userCount != 0:
        tmp = userCount
        userCount = len(col.find({'session':{'$gt':sessionCount}}).distinct('user_id'))
        if userCount != preUserCount:
            userCounts[len(userCounts)-1] = userCounts[len(userCounts)-1] - preUserCount
            userCounts.append(preUserCount)
            sessionCounts.append(prevSessionCount)
        preUserCount = userCount
        prevSessionCount = sessionCount
        # print ("%s - %s" % (sessionCount, userCount), end='\r')
        sessionCount += 1
        helpers.printProgress(sessionCount,1144)
    # print (userCounts)
    # print (sessionCounts)
    # userCounts.append(1000)
    # sessionCounts.append(838)
    xticks = helpers.makeTicks(yMax=sessionCount)
    return userCounts[2:],sessionCounts[1:],xticks

def sessionCountGroups():
    reducer = Code("""
        function (cur,result) {
            result.count += 1
        }
    """)
    groups = col.group(
       key={'session':1},
       condition={},
       reduce=reducer,
       initial={'count':0}
    )
    print (groups)
    sys.exit()

if __name__ == "__main__":
    main()
