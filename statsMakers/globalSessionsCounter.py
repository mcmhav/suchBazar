import csv
import argparse
import sys
import helpers
import matplotlib.pyplot as plt
import os
from bson import Binary, Code
import numpy as np

def main(sessDB='sessionsNew'):
    # sessionCountGroups()
    # ks,counts,xticks = sessionCountDistrCum(sessDB)
    # helpers.makePlot(
    #     'sessionsCount',
    #     ks,
    #     counts,
    #     title='Global Sessions Count',
    #     ylabel='Count of Users',
    #     xlabel='Count of Sessions',
    #     show=True,
    #     grid=True,
    #     xticks=[xticks,xticks]
    # )
    # sys.exit()
    # xticks = helpers.makeTicks(yMax=1140)
    # print (list(xticks))
    # print ([xticks,xticks])
    # tm = np.array([xticks,xticks])
    # print (tm)
    # # sys.exit()
    # yaxis = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 50, 51, 53, 54, 55, 56, 58, 60, 65, 67, 68, 70, 71, 75, 79, 80, 87, 88, 92, 94, 99, 100, 110, 111, 115, 116, 118, 119, 125, 126, 128, 134, 141, 144, 147, 150, 156, 163, 187, 206, 322, 388, 523, 573, 695, 1142]
    # xaxis = [404, 231, 215, 153, 151, 110, 90, 78, 59, 49, 45, 45, 23, 26, 28, 13, 25, 24, 16, 8, 20, 10, 14, 12, 3, 12, 11, 7, 7, 6, 11, 3, 4, 3, 2, 2, 6, 5, 3, 7, 3, 4, 1, 3, 2, 4, 3, 2, 4, 1, 1, 1, 2, 1, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # xticks = [0, 100, 300, 400, 1000]

    # print (len(xaxis))
    xaxis,yaxis,xticks = handle_appStarted(sessDB)
    helpers.makePlot(
        'sessionsCount',
        yaxis,
        xaxis,
        # title='Global Sessions Count',
        ylabel='Amount of Users',
        xlabel='Session count',
        show=False,
        grid=True,
        xticks=[helpers.makeTicks(yMax=len(xaxis)),xticks]
    )

def sessionCountDistrCum(sessDB):
    groups = helpers.getKGroups('session',sessDB)
    groups_sorted = sorted(groups, key=lambda k: k['count'],reverse=True)
    ks = [int(x['session']) for x in groups_sorted]
    counts = [int(x['count']) for x in groups_sorted]
    # for c in counts:
    #     print (c)

    # sys.exit()
    print (ks)
    print ()
    print (counts_sorted)
    xticks = helpers.makeTicks(yMax=max(ks))
    return ks,counts,xticks


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
