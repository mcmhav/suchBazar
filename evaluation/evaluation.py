'''
Evaluation functions

'''

import argparse

#Evaluation modules
import coverage
import eventStats as es
import helpers
import auc
import map
import helpers
import coldStart
#import hlu
#import ndcg
import itemAverage
import filterbots as fb
import ntpath
import sys
import time
from multiprocessing import Process


def evaluation():
    '''
    Run Evaluation of the different cold-start splits
    '''

    #evaluate('../data/system_train1.txt', '../data/system_test.txt', '../mahout/testikus.txt')
    #evaluate('../data/system_train2.txt', '../data/system_test.txt', '../mahout/testikus.txt')
    #evaluate('../data/system_train3.txt', '../data/system_test.txt', '../mahout/testikus.txt')
    #evaluate('../data/user_train1.txt', '../data/user_test1.txt', '../mahout/testikus.txt')
    #evaluate('../data/user_train2.txt', '../data/user_test2.txt', '../mahout/testikus.txt')
    #evaluate('../data/user_train3.txt', '../data/user_test3.txt', '../mahout/testikus.txt')
    #evaluate('../data/item_train1.txt', '../data/item_test1.txt', '../mahout/testikus.txt')
    #evaluate('../data/item_train2.txt', '../data/item_test2.txt', '../mahout/testikus.txt')
    #evaluate('../data/item_train3.txt', '../data/item_test3.txt', '../mahout/testikus.txt')

    #evaluate('../data/ftrain.txt', '../data/user_test3.txt', '../data/predictions.txt')
    #evaluate('../generators/train.csv', '../generators/test.csv', '../mahout/testikus.txt')
    #evaluate('../generators/train.csv', '../generators/test.csv', '../generators/predictions.txt')

def testCases():
    '''
    Runs the testcases for the various evaluation metrics
    '''

    #runTestCases()

def coldStartSplits():
    '''
    Functions for creating cold-start evaluation dataset splits
    '''

    #Settings
    filterBotSettings = [0,0,0,0,0]
    timeStamps = True

    createColdStartSplits('../generators/ratings/count_sigmoid_fixed_sr-3.5.txt', timeStamps, filterBotSettings)
    #createColdStartSplits('../generators/ratings/count_linear.txt', timeStamps, filterBotSettings)
    #createColdStartSplits('../generators/ratings/count_sigmoid_constant_sc-30.0.txt', timeStamps, filterBotSettings)
    #createColdStartSplits('../generators/ratings/count_sigmoid_fixed_sr-4.5.txt', timeStamps, filterBotSettings)
    #createColdStartSplits('../generators/ratings/naive.txt', timeStamps, filterBotSettings)
    #createColdStartSplits('../generators/ratings/recentness_linear.txt', timeStamps, filterBotSettings)
    #createColdStartSplits('../generators/ratings/recentness_sigmoid_constant_sc-30.0.txt', timeStamps, filterBotSettings)
    #createColdStartSplits('../generators/ratings/recentness_sigmoid_fixed_sr-4.5.txt', timeStamps, filterBotSettings)

def evaluate(trainFile, testFile, predictionFile, k, l, beta, m, featurefile):
    start = time.time()

    train = helpers.readRatingsFromFile(trainFile, convert=False)
    test = helpers.readRatingsFromFile(testFile, convert=False)


    if not predictionFile:
        if not featurefile or not os.path.isfile(featurefile):
	    print("Can not evaluate without featurefile, when I dont even have a predictionfile!")
            sys.exit(1)
        train = fb.addFilterBotRatings(train, featurefile, fbots=[1, 1, 1, 1, 0])
        #predictions = itemAverage.itemAverage(train, test)
        predictions = itemAverage.mostPopular(train, test)

    else:
        if m:
            predictions = helpers.readMyMediaLitePredictions(predictionFile)
        else:
            predictions = helpers.readRatingsFromFileSmart(predictionFile)

    # we use approx. 15 seconds to come here.
    us_coverage, is_coverage = coverage.compute(train, predictions)
    candidateItems = helpers.getUniqueItemList(train)

    #Build Hashmaps
    train = helpers.buildDictByIndex(train, 0)
    test = helpers.buildDictByIndex(test, 0)
    predictions = helpers.buildDictByIndex(predictions, 0) # takes about 5 seconds to complete.
    predictions = helpers.sortDictByRatings(predictions)
    roc_auc = auc.compute(train, test, predictions, candidateItems)
    t, p = helpers.preprocessMAP(test, predictions, k)

    mapk = map.mapk(t, p, k)
    #t, p = helpers.preprocessDCG(test, predictions, l)
    #nDCG = ndcg.compute(t, p, 1, l)
    #hluB = hlu.compute(t, p, beta)

    eStats = es.compute(test, predictions, k)

    #print('*** RESULTS ***')
    #print('User-Space Coverage: %.4f\nItem-Space Coverage: %.4f' %(us_coverage, is_coverage))
    #print('AUC: %.4f' %(roc_auc))
    #print('MAP%d: %.4f' %(k, mapk))
    #print('nDCG%d: %.4f' %(l, nDCG))
    #print('HLU%d: %.4f' %(beta, hluB))
    print('Evaluation took %.2f seconds.'%(time.time()-start))

    helpers.prepareEvauationScoreToLaTeX(
        ntpath.basename(predictionFile),
        str(us_coverage),
        str(is_coverage),
        str(roc_auc),
        str(mapk),
        eStats,
        str(k),
    )

def createColdStartSplits(ratingFile, timestamps, featurefile, fbConfig):

    ratings = helpers.readRatingsFromFileSmart(ratingFile, False)
    filename = ratingFile.split('/')[-1].split('.')[0]
    procs = []

    print('Generating cold-start user dataset splits...')
    addToParallelRun(procs, coldStart.generateColdStartSplits, filename, ratings, 'user', 0.1, 20, featurefile, [0.10, 0.40, 0.75], timestamps, fbConfig)
    print('Generating cold-start item dataset splits...')
    addToParallelRun(procs, coldStart.generateColdStartSplits, filename, ratings, 'item', 0.05, 15, featurefile, [0.10, 0.40, 0.75], timestamps, fbConfig)
    print('Generating cold-start system dataset splits...')
    addToParallelRun(procs, coldStart.generateColdStartSystemSplits, filename, ratings, 0.20, featurefile, [0.4, 0.6, 0.8], timestamps, fbConfig)

    # combine jobs
    for p in procs:
        p.join()
    print('Done!')

def addToParallelRun(procs, method, *args):
    '''
    Run procs parallel
    '''
    p = Process(target=method, args=args)
    p.start()
    procs.append(p)

def runTestCases():
    '''
    Function for comparing different Rank Accuracy Metrics
    on a set of test cases
    '''

    test_case_actual = []
    test_case_pred = []

    test_case_actual.append([1,2,3,4])
    test_case_pred.append([0,1,0,0])

    test_case_actual.append([1,2,3,4])
    test_case_pred.append([2,0,3,1])

    test_case_actual.append([1,2,3,4])
    test_case_pred.append([0,1,2,3])

    test_case_actual.append([1,2,3,4,5,6,7,8,9,10])
    test_case_pred.append([1,2,3,4,5,6,7,8,9,10])

    test_case_actual.append([1,2,3,4,5,6,7,8,9,10])
    test_case_pred.append([10,9,8,7,6,5,4,3,2,1])

    test_case_actual.append([1,2,3,4,5,6,7,8,9,10])
    test_case_pred.append([10,5,4,3,1,2,8,7,6,9])

    test_case_actual.append([1,2,3,4,5,6,7,8,9,10])
    test_case_pred.append([1,12,14,3,16,18,66,52,22,11])

    test_case_actual.append([1,2,3,4,5,6,7,8,9,10])
    test_case_pred.append([4,15,44,8,19,22,23,13,14,15])

    test_case_actual.append([1,2,3,4,5,6,7,8,9,10])
    test_case_pred.append([19,17,15,14,5,22,13,12,11,10])

    test_case_actual.append([1,2,3,4,5,6,7,8,9,10])
    test_case_pred.append([33,44,11,12,17,22,13,14,9,10])

    for actual, pred in zip(test_case_actual, test_case_pred):
        print('MAP10 - Test case 1: %.2f' %map.apk(actual, pred, 10))
        print('nDCG - Test case 1: %.2f' %ndcg.compute(actual, pred, 0))
        print('Spearman - Test case 2: %.2f' %stats.spearmanr(actual, pred)[0])
        print('Kendall - Test case 2: %.2f' %stats.kendalltau(actual, pred)[0])

parser = argparse.ArgumentParser(description='Evaluate Recommender Systems')
parser.add_argument('--coldstart-split', dest='coldstart', type=str, help="Defaulting to ...")
parser.add_argument('-fb', dest='fbConfig', type=str, help="Defaulting to ...")
parser.add_argument('-t', dest='timestamps', default=False, action="store_true", help="Defaultign to...")


parser.add_argument('--test-file', dest='test', type=str, help="Defaulting to ...")
parser.add_argument('--training-file', dest='train', type=str, help="Defaulting to ...")
parser.add_argument('--prediction-file', dest='pred', type=str, help="Defaulting to ...")
parser.add_argument('--feature-file', dest='featurefile', type=str, help="Defaulting to ...")
parser.add_argument('-k', dest='k', type=int, default=20, help='Defaulting to...')
parser.add_argument('-l', dest='l', type=int, default=20, help='Defaulting to...')
parser.add_argument('-b', dest='beta', type=int, default=2, help='Defaulting to...')
parser.add_argument('-m', dest='m', default=False, action="store_true", help="Defaultign to...")

args = parser.parse_args()

if args.coldstart:
    fb = [0,0,0,0,0]
    if args.fbConfig:
        fb = args.fbConfig.split(',')
        fb = [int(x) for x in fb]
        if(len(fb) < 5):
            print('Five arguments must be given, defaulting to [0,0,0,0,0]')
            fb = [0,0,0,0,0]
    createColdStartSplits(args.coldstart, args.timestamps, args.featurefile, fb)

if args.test:
    evaluate(args.train, args.test, args.pred, args.k, args.l, args.beta, args.m, args.featurefile)
