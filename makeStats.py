import sys
import argparse
# import helpers
from bson import Binary, Code
from mongoDBAdders import *
from statsMakers import priceDistibution
from statsMakers import eventPerDay
from statsMakers import simpleGeoPlotter
from statsMakers import eventCountDistributions
from statsMakers import huntNegativeFeedback
from statsMakers import itemTimeSpan
from statsMakers import timeSpentOnItemBeforeAction
from statsMakers import ratingsPerUser
from statsMakers import userAges
from statsMakers import makeSimpleStats

def main():
    print ("start")
    db = 'sessionsNew3'
    show = False
    save = True
    makeNew = False
    eventCountDistributions.main(sessDB=db,show=show, save=save)
    eventPerDay.main(sessDB=db,show=show, save=save)
    huntNegativeFeedback.main(sessDB=db,show=show, save=save, makeNew=makeNew)

    itemTimeSpan.main(sessDB=db,show=show, save=save)

    priceDistibution.main(sessDB=db,show=show, save=save)
    ratingsPerUser.main(sessDB=db,show=show, save=save)
    simpleGeoPlotter.main(sessDB=db,show=show, save=save)
    timeSpentOnItemBeforeAction.main(sessDB=db,makeNew=makeNew,show=show, save=save)
    userAges.main(sessDB=db,show=show, save=save)
    makeSimpleStats.main(sessDB=db)
    print ("Done!")


if __name__ == "__main__":
    main()
