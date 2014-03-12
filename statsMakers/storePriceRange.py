import csv
import argparse
import sys
import helpers

parser = argparse.ArgumentParser(description='')
parser.add_argument('-v',dest='v', action='store_true')
parser.add_argument('-c',type=str, default="offer")
parser.add_argument('-d',type=str, default="stats")
parser.set_defaults(v=False)
args = parser.parse_args()

print ("Verbose:         %s" % args.v)
print ("Collection used: %s" % args.c)

col = helpers.getCollection(args.c)

def main():
    handle_appStarted()

def handle_appStarted():
    userCount = -1
    sessionCount = 0
    c = helpers.getCSVWriter(args.d + '/' + 'sessionsCounts')
    prevSessionCount = 'SessionCount'
    preUserCount = 'UserCount'
    while userCount != 0:
        tmp = userCount
        userCount = len(col.find({'session':{'$gt':sessionCount}}).distinct('user_id'))
        if userCount != preUserCount:
            c.writerow([prevSessionCount, preUserCount])
        preUserCount = userCount
        prevSessionCount = sessionCount
        if args.v:
            print ("%s - %s" % (sessionCount, userCount), end='\r')
        sessionCount += 1

    helpers.closeF()


if __name__ == "__main__":
    main()
