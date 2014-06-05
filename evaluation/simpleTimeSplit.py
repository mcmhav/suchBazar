import csv
import sys
import os
import argparse
import helpers
from operator import itemgetter

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)
SPLITS_FOLDER = 'splits'
GENERATED_LOCATION = 'generated'
folder = ROOT_FOLDER + '/' + GENERATED_LOCATION + '/' + SPLITS_FOLDER + '/'

def timeSplit(inputFile, test_ratio):
    '''
    Split the dataset on time, putting the freshest
    ratings in the testset
    '''
    ratings = helpers.readRatingsFromFile(inputFile)
    
    if len(ratings[0]) <= 3:
        print('The file does not contain timestamps, doing a traditional split')
    else:
        ratings = sorted(ratings, key=itemgetter(3), reverse=False)  #Sort ratings based on timestamps, the freshest being 'on top'
    num_test_ratings = int(len(ratings)*test_ratio)                 #Number of ratings to use for testing
    test = ratings[-num_test_ratings:]                              #Put freshest ratings in the testset
    train = ratings[:-num_test_ratings]
    
    input = inputFile.split('/')[-1]
    input = "-".join(input.split('.')[:-1])
    
    helpers.writeRatingsToFile('%s%s_timetrain.txt' %(folder, input), train, )
    helpers.writeRatingsToFile('%s%s_timetest.txt' %(folder, input), test)


parser = argparse.ArgumentParser(description='Create time-based dataset split')
parser.add_argument('-i', dest='i', type=str, help="Defaulting to ...")
parser.add_argument('-s', dest='s', type=float, default=0.2, help='Defaulting to 0.1')
args = parser.parse_args()

if not args.i:
    print ("Please specify an input file")
    sys.exit(1)
    
timeSplit(args.i, args.s)