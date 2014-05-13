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

def main():
    
    #evaluate('../generators/train.csv', '../generators/test.csv', '../mahout/testikus.txt')
    evaluate('../generators/train.csv', '../generators/test.csv', '../generators/predictions.txt')
    #runTestCases()
    #coldStartEvaluation('../generators/train.csv')

def evaluate(trainFile, testFile, predictionFile):
    
    k = 50
    
    train = helpers.readRatingsFromFile(trainFile)
    test = helpers.readRatingsFromFile(testFile)
    #predictions = helpers.readRatingsFromFile(predictionFile)
    predictions = helpers.readMyMediaLitePredictions(predictionFile)
    
    us_coverage, is_coverage = coverage.compute(train, predictions)
    roc_auc = auc.compute(train, test, predictions)
    map10 = map.mapk(test, predictions, k)
    
    print('*** RESULTS ***')
    print('User-Space Coverage: %.4f\nItem-Space Coverage: %.4f' %(us_coverage, is_coverage))
    print('AUC: %.4f' %(roc_auc))
    print('MAP%d: %.4f' %(k, map10))
    
    
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
        
    test_case_1_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_1_pred =      [1,2,3,4,5,6,7,8,9,10]
    
    test_case_2_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_2_pred =      [10,9,8,7,6,5,4,3,2,1]
    
    test_case_3_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_3_pred =      [1,2,11,12,16,18,44,77,55,19]
    
    test_case_4_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_4_pred =      [11,12,14,15,16,18,66,52,1,2]
    
    test_case_5_actual =    [1,2,3,4,5,6,7,8,9,10]
    test_case_5_pred =      [12,15,44,4,17,22,8,7,6,5]
    
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
    print('Spearman - Test case 2: %.2f' %stats.spearmanr(test_case_1_actual, test_case_1_pred)[0])
    print('Kendall - Test case 2: %.2f' %stats.kendalltau(test_case_1_actual, test_case_1_pred)[0])
    
    print('MAP10 - Test case 2: %.2f' %map.apk(test_case_2_actual, test_case_2_pred, 10))
    print('nDCG - Test case 2: %.2f' %edrc.nDCG(test_case_2_actual, test_case_2_pred, 0))
    print('Spearman - Test case 2: %.2f' %stats.spearmanr(test_case_2_actual, test_case_2_pred)[0])
    print('Kendall - Test case 2: %.2f' %stats.kendalltau(test_case_2_actual, test_case_2_pred)[0])
    
    print('MAP10 - Test case 3: %.2f' %map.apk(test_case_3_actual, test_case_3_pred, 10))
    print('nDCG - Test case 3: %.2f' %edrc.nDCG(test_case_3_actual, test_case_3_pred, 0))
    print('Spearman - Test case 2: %.2f' %stats.kendalltau(test_case_3_actual, test_case_3_pred)[0])
    print('Kendall - Test case 2: %.2f' %stats.spearmanr(test_case_3_actual, test_case_3_pred)[0])
    
    print('MAP10 - Test case 4: %.2f' %map.apk(test_case_4_actual, test_case_4_pred, 10))
    print('nDCG - Test case 4: %.2f' %edrc.nDCG(test_case_4_actual, test_case_4_pred, 0))
    print('Spearman - Test case 2: %.2f' %stats.spearmanr(test_case_4_actual, test_case_4_pred)[0])
    print('Kendall - Test case 2: %.2f' %stats.kendalltau(test_case_4_actual, test_case_4_pred)[0])

if __name__ == "__main__":
    main()