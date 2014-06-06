import datetime
import sys
import argparse
import helpers
from bson import Binary, Code
import numpy as np
import os.path

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)
DATA_FOLDER = 'data'
folder = SCRIPT_FOLDER + '/' + DATA_FOLDER

if not os.path.exists(folder):
        os.makedirs(folder)

def main(sessDB='sessionsNew'):
    col = helpers.getCollection(sessDB)
    findTimeFor("product_detail_clicked",col)

def findTimeFor(action,col):

    if os.path.isfile(folder + '/' + action + '.csv'):
        avgTimeForUser = getActionFile(action)
    else:
        avgTimeForUser = findUserAVGS(action,col)
        writeUserAverages(avgTimeForUser,action)

    helpers.plotAverageSomething(
        avgTimeForUser,
        action,
        # title='Bounce rate',
        ylabel='Amount of Users',
        xlabel='View time',
        show=False,
        capAtEnd=True,
        capVal=70,
        # addCapped=True
    )

def findUserAVGS(action,col):
    users = col.distinct('user_id')
    total = len(users)
    globalTot = 0
    zeroC = 0
    wtf = 0
    count = 0
    avgTimeForUser = []
    # e = open("ignoreTime" + '.csv','w')
    for user in users:
        userEvents = col.find({'user_id':user}).sort('ts',1)
        avgViewTimeOnIgnoredItem = 0
        viewTimeStart = -1
        viewedItem = ''
        viewedItemSession = -1
        c = 0

        for event in userEvents:
            # print ("%s - %s" % (event['event_id'],event['ts']))
            if event['event_id'] == action:
                viewTimeStart = event['ts']
                viewedItem = event['product_id']
                viewedItemSession = event['session']
            if viewTimeStart != -1 and event['session'] == viewedItemSession and event['product_id'] != viewedItem:
                avgViewTimeOnIgnoredItem += (event['ts'] - viewTimeStart)
                viewTimeStart = -1
                viewedItemSession = -1
            c += 1

        # if avgViewTimeOnIgnoredItem == 0:
        #     sys.exit()
        # for sessionN in sessions:
        #     sessionEvents = col.find({'user_id':user,'session':sessionN})
        #     for event in sessionEvents:
        #         continue
                # print (event)
        if avgViewTimeOnIgnoredItem > 0:
            globalTot += avgViewTimeOnIgnoredItem/c
            # e.write("uid" + str(user) + "," + str(avgViewTimeOnIgnoredItem/c) + "\n")
            avgTimeForUser.append(float(avgViewTimeOnIgnoredItem/c))
            wtf += 1
            # print (wtf)
        else:
            zeroC += 1
        # print (avgViewTimeOnIgnoredItem)
        count += 1
        helpers.printProgress(count,total)

    print ()
    print (globalTot/(count-zeroC))
    print (wtf)
    print (zeroC)
    print (count)
    print (globalTot)
    # e.close()
    return avgTimeForUser

def getActionFile(action):
    e = open(folder + "/" + action + '.csv','r')
    line = e.readlines()
    e.close()
    userAverages = []
    for ua in line[0].split(','):
        try:
            userAverages.append(float(ua))
        except:
            print ('lol')
    return userAverages

def writeUserAverages(avg,name):
    e = open(folder + '/' + name + '.csv','w')
    for av in avg:
        e.write(str(av) + ", ")
    e.close()

if __name__ == "__main__":
    main()
