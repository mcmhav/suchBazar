import sys
import argparse
# import helpers
from bson import Binary, Code
from mongoDBAdders import *
from statsMakers import priceDistibution
from statsMakers import eventPerDay
from statsMakers import simpleGeoPlotter
from statsMakers import globalSessionsCounter

def main():
    print ("start")
    # statsMakers.helpers
    # statsMakers.helpers
    priceDistibution.main()
    eventPerDay.main()
    simpleGeoPlotter.main()
    globalSessionsCounter.main()


if __name__ == "__main__":
    main()
