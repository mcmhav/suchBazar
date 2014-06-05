import sys
import argparse
# import helpers
from bson import Binary, Code
from mongoDBAdders import *
from statsMakers import priceDistibution
from statsMakers import eventPerDay
from statsMakers import simpleGeoPlotter
from statsMakers import globalSessionsCounter
from statsMakers import eventCountDistributions
from statsMakers import huntNegativeFeedback
from statsMakers import itemTimeSpan
from statsMakers import timeSpentOnItemBeforeAction
from statsMakers import ratingsPerUser
from statsMakers import userAges
# from statsMakers import makeSimpleStats

def main():
    print ("start")
    priceDistibution.main()
    eventPerDay.main()
    simpleGeoPlotter.main()
    globalSessionsCounter.main()
    eventCountDistributions.main()
    huntNegativeFeedback.main()
    itemTimeSpan.main()
    timeSpentOnItemBeforeAction.main()
    ratingsPerUser.main()
    userAges.main()
    # makeSimpleStats.main()
    print ("Done!")


if __name__ == "__main__":
    main()
