'''



'''

import argparse
import numpy as np
from sklearn import metrics

#Evaluation modules
import coverage
import helpers
import areaUnderCurve as auc
import meanap as map
import coldStartDatasetGenerator as coldStart
import expectedDiscountedRankCorrelation as edrc
#import meanPercentageRanking
#import coldStartDatasetGenerator





def main():

    #evaluate('../generators/train.csv', '../generators/test.csv', '../mahout/testikus.txt')
    testCases()

def evaluate(trainFile, testFile, predictionFile):

    train = helpers.readRatingsFromFile(trainFile)
    test = helpers.readRatingsFromFile(testFile)
    predictions = helpers.readRatingsFromFile(predictionFile)

    us_coverage, is_coverage = coverage.measureCoverage(train, predictions)
    roc_auc = auc.AUC(train, test, predictions)
    map10 = map.mapk(test, predictions, 10)
    #Measure nDCG
    #Measure MAP
    #Measure MPR

    print('User-Space Coverage: %.2f\nItem-Space Coverage: %.3f' %(us_coverage, is_coverage))
    print('Area Under Curve (AUC): %.2f' %(roc_auc))
    print('Mean Average Precision: %.2f' %(map10))


def coldStartEvaluation(ratingFile):

    ratings = helpers.readRatingsFromFile(ratingFile)
    coldStart.generateColdStartSplits(ratings, 'user', 0.1, [10, 15, 20])
    coldStart.generateColdStartSplits(ratings, 'item', 0.02, [5, 10, 15])
    coldStart.generateColdStartSystemSplits(ratings, 0.20, [0.4, 0.6, 0.8], False)

def testCases():

    #MRR

    test_case_1_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_1_pred =      [1,2,3,4,5,6,7,8,9,10]

    test_case_2_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_2_pred =      [10,9,8,7,6,5,4,3,2,1]

    test_case_3_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_3_pred =      [1,2,11,12,16,18,44,77,55,19]

    test_case_4_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_4_pred =      [11,12,14,15,16,18,66,52,1,2]

    test_case_5_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_5_pred =      [10,9,3,4,17,22,8,7,6,5]

    test_case_6_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_6_pred =      [10,9,3,4,17,22,8,7,6,5]

    test_case_7_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_7_pred =      [10,9,3,4,17,22,8,7,6,5]

    test_case_8_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_8_pred =      [10,9,3,4,17,22,8,7,6,5]

    test_case_9_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_9_pred =      [10,9,3,4,17,22,8,7,6,5]

    test_case_10_actual =   [1,2,3,4,5,6,7,8,9,10]
    test_case_10_pred =     [10,9,3,4,17,22,8,7,6,5]



    print('MAP10 - Test case 1: %.2f' %map.apk(test_case_1_actual, test_case_1_pred, 10))
    print('nDCG - Test case 1: %.2f' %edrc.nDCG(test_case_1_actual, test_case_1_pred, 0))

    print('MAP10 - Test case 2: %.2f' %map.apk(test_case_2_actual, test_case_2_pred, 10))
    print('nDCG - Test case 2: %.2f' %edrc.nDCG(test_case_2_actual, test_case_2_pred, 0))

    print('MAP10 - Test case 3: %.2f' %map.apk(test_case_3_actual, test_case_3_pred, 10))
    print('nDCG - Test case 3: %.2f' %edrc.nDCG(test_case_3_actual, test_case_3_pred, 0))

    print('MAP10 - Test case 4: %.2f' %map.apk(test_case_4_actual, test_case_4_pred, 10))
    print('nDCG - Test case 4: %.2f' %edrc.nDCG(test_case_4_actual, test_case_4_pred, 0))


if __name__ == "__main__":
    main()
