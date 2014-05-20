'''
Evaluation functions

'''

from sklearn import metrics
from scipy import stats
from operator import itemgetter

#Evaluation modules
import coverage
import helpers
import auc
import map
import coldStart
import hlu
import ndcg
import itemAverage
import filterbots as fb

def main():

    #evaluate('../data/system_train1.txt', '../data/system_test.txt', '../mahout/testikus.txt')
    #evaluate('../data/system_train2.txt', '../data/system_test.txt', '../mahout/testikus.txt')
    #evaluate('../data/system_train3.txt', '../data/system_test.txt', '../mahout/testikus.txt')
    #evaluate('../data/user_train1.txt', '../data/user_test1.txt', '../mahout/testikus.txt')
    #evaluate('../data/user_train2.txt', '../data/user_test2.txt', '../mahout/testikus.txt')
    evaluate('../data/user_train3.txt', '../data/user_test3.txt', '../mahout/testikus.txt')
    #evaluate('../data/item_train1.txt', '../data/item_test1.txt', '../mahout/testikus.txt')
    #evaluate('../data/item_train2.txt', '../data/item_test2.txt', '../mahout/testikus.txt')
    #evaluate('../data/item_train3.txt', '../data/item_test3.txt', '../mahout/testikus.txt')
    
    
    #evaluate('../data/ftrain.txt', '../data/user_test3.txt', '../data/predictions.txt')
    #evaluate('../generators/train.csv', '../generators/test.csv', '../generators/predictions.txt')
    
    
    #runTestCases()
    
    #coldStartEvaluation('../generators/ratings/count_linear.txt')
    #coldStartEvaluation('../generators/ratings/count_linear.txt')
    #coldStartEvaluation('../generators/ratings/count_sigmoid_constant_sc-30.0.txt')
    #coldStartEvaluation('../generators/ratings/count_sigmoid_fixed_sr-4.5.txt')
    #coldStartEvaluation('../generators/ratings/naive.txt')
    #coldStartEvaluation('../generators/ratings/recentness_linear.txt')
    #coldStartEvaluation('../generators/ratings/recentness_sigmoid_constant_sc-30.0.txt')
    #coldStartEvaluation('../generators/ratings/recentness_sigmoid_fixed_sr-4.5.txt')
    

def evaluate(trainFile, testFile, predictionFile):

    k = 100
    beta = 2

    #train = helpers.readRatingsFromFile(trainFile)
    train = helpers.readRatings(trainFile, True)
    test = helpers.readRatingsFromFile(testFile)
    predictions = helpers.readRatingsFromFile(predictionFile)

    train = fb.addFBRatings(train, 1, 1, 1, 1, 1)
    #predictions = itemAverage.compute(train, test)
    predictions = itemAverage.mostPopular(train, test)

    us_coverage, is_coverage = coverage.compute(train, predictions)
    roc_auc = auc.compute(train, test, predictions)
    t, p = generatePrecisionLists(test, predictions, k)
    mapk = map.mapk(t, p, k)
    t, p = generatenDCGLists(test, predictions, k)
    nDCG = ndcg.compute(t, p, 1, k)
    hluB = hlu.compute(test, predictions, beta)

    print('*** RESULTS ***')
    print('User-Space Coverage: %.4f\nItem-Space Coverage: %.4f' %(us_coverage, is_coverage))
    print('AUC: %.4f' %(roc_auc))
    print('MAP%d: %.4f' %(k, mapk))
    print('nDCG%d: %.4f' %(k, nDCG))
    print('HLU%d: %.4f' %(beta, hluB))


def coldStartEvaluation(ratingFile):

    ratings = helpers.readRatingsFromFile(ratingFile, True)
    print('Generating cold-start user dataset splits...')
    coldStart.generateColdStartSplits(ratings, 'user', 0.1, [10, 15, 20], True)
    print('Generating cold-start item dataset splits...')
    coldStart.generateColdStartSplits(ratings, 'item', 0.02, [5, 10, 15], True)
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
        
    
def generatePrecisionLists(actual, predictions, k):
    '''
    Preprocessing nMAP calculations
    
    '''
    
    a = helpers.buildDictByIndex(actual, 0)
    p = helpers.buildDictByIndex(predictions, 0)
    pred = []
    test = []
    for user in a:
        utest = []
        for i in range(len(a[user])):
            utest.append(a[user][i][1])
        test.append(utest)
        if user in p:
            upred = []
            p[user] = sorted(p[user], key=itemgetter(2), reverse=True)
            for j in range(k):
                upred.append(p[user][j][1])
            pred.append(upred)
    return test, pred

def generatenDCGLists(actual, predictions, k):
    '''
    Preprocessing nDCG calculations
    
    '''
    
    a = helpers.buildDictByIndex(actual, 0)
    p = helpers.buildDictByIndex(predictions, 0)
    pred = []
    test = []
    for user in a:
        utest = []
        for i in range(len(a[user])):
            utest.append([a[user][i][1], a[user][i][2]])
        test.append(utest)
        if user in p:
            upred = []
            p[user] = sorted(p[user], key=itemgetter(2), reverse=True)
            for j in range(k):
                upred.append([p[user][j][1], p[user][i][2]])
            pred.append(upred)
    return test, pred 

if __name__ == "__main__":
    main()
