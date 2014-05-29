import csv
import argparse
import sys
import helpers
import matplotlib.pyplot as plt
import os
from bson import Binary, Code

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
    xaxis,yaxis,xticks = handle_appStarted(sessDB)
    helpers.makePlot(
        'sessionsCount',
        yaxis,
        xaxis,
        title='Global Sessions Count',
        ylabel='Amount of Users',
        xlabel='Session count',
        show=True,
        grid=True,
        xticks=[xticks,xticks]
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
        print ((sessionCount/1144)*100)
    # print (userCounts)
    # print (sessionCounts)
    # userCounts.append(1000)
    # sessionCounts.append(838)
    xticks = helpers.makeTicks(yMax=sessionCount,steps=10)
    print (xticks)
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

def makePlot(xaxis,yaxis):
    width = 0.6
    fig, ax = plt.subplots()
    fig.set_size_inches(14.0,8.0)
    # plt.axis([0, count, 0, 2500])
    ax.bar(yaxis, xaxis, width=width)
    # ax.set_xticks(yaxis)
    # ax.set_xticklabels(yaxis_labels)
    # fig.autofmt_xdate()
    # fig = plt.figure(figsize=(4, 5), dpi=100)

    plt.grid(True)


    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/sessionsCount.png"
    plt.savefig(location)
    plt.show()
    print ("Sessions count written to: %s" % location)

if __name__ == "__main__":
    main()
