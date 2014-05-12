import csv
import argparse
import sys
import helpers
import matplotlib.pyplot as plt
import os
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Constructs overview of how many sessions users have.')
parser.add_argument('-c',type=str, default="sessions")
parser.add_argument('-d',type=str, default="stats")
args = parser.parse_args()

print ("Collection used: %s" % args.c)

col = helpers.getCollection(args.c)

def main():
    # sessionCountGroups()
    xaxis,yaxis = handle_appStarted()
    makePlot(xaxis,yaxis)

def handle_appStarted():
    userCount = -1
    sessionCount = 0
    c = helpers.getCSVWriter(args.d + '/' + 'sessionsCounts')
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
            c.writerow([prevSessionCount, preUserCount])
            userCounts[len(userCounts)-1] = userCounts[len(userCounts)-1] - preUserCount
            userCounts.append(preUserCount)
            sessionCounts.append(prevSessionCount)
        preUserCount = userCount
        prevSessionCount = sessionCount
        # print ("%s - %s" % (sessionCount, userCount), end='\r')
        sessionCount += 1
    helpers.closeF()
    print (userCounts)
    print (sessionCounts)
    # userCounts.append(1000)
    # sessionCounts.append(838)
    return userCounts[2:],sessionCounts[1:]

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
    plt.title('Global Sessions Count')
    plt.ylabel('Count of Users')
    plt.xlabel('Count of Sessions')
    plt.grid(True)


    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/sessionsCount.png"
    plt.savefig(location)
    print ("Sessions count written to: %s" % location)

if __name__ == "__main__":
    main()
