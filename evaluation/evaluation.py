'''
Evaluation functions

'''

from sklearn import metrics
from scipy import stats

#Evaluation modules
import coverage
import helpers
import auc
import map
import coldStart
import edrc
import hlu

def main():

    evaluate('../generators/train.csv', '../generators/test.csv', '../mahout/testikus.txt')

    #evaluate('../generators/train.csv', '../generators/test.csv', '../generators/predictions.txt')
    #runTestCases()
    #coldStartEvaluation('../generators/train.csv')

def evaluate(trainFile, testFile, predictionFile):

    k = 50
    beta = 2

    train = helpers.readRatingsFromFile(trainFile)
    test = helpers.readRatingsFromFile(testFile)
    predictions = helpers.readRatingsFromFile(predictionFile)
    # predictions = helpers.readMyMediaLitePredictions(predictionFile)

    us_coverage, is_coverage = coverage.compute(train, predictions)
    roc_auc = auc.compute(train, test, predictions)
    map10 = map.mapk(test, predictions, k)
    hluB = hlu.compute(test, predictions, beta)

    print('*** RESULTS ***')
    print('User-Space Coverage: %.4f\nItem-Space Coverage: %.4f' %(us_coverage, is_coverage))
    print('AUC: %.4f' %(roc_auc))
    print('MAP%d: %.4f' %(k, map10))
    print('HLU%d: %.4f' %(beta, hluB))


def coldStartEvaluation(ratingFile):

    ratings = helpers.readRatingsFromFile(ratingFile)
    print('Generating cold-start user dataset splits...')
    coldStart.generateColdStartSplits(ratings, 'user', 0.1, [10, 15, 20])
    print('Generating cold-start item dataset splits...')
    coldStart.generateColdStartSplits(ratings, 'item', 0.02, [5, 10, 15])
    print('Generating cold-start system dataset splits...')
    coldStart.generateColdStartSystemSplits(ratings, 0.20, [0.4, 0.6, 0.8], False)
    print('Done!')

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
        #print('nDCG - Test case 1: %.2f' %edrc.nDCG(actual, pred, 0))
        #print('Spearman - Test case 2: %.2f' %stats.spearmanr(actual, pred)[0])
        #print('Kendall - Test case 2: %.2f' %stats.kendalltau(actual, pred)[0])

if __name__ == "__main__":
    main()
