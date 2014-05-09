import numpy as np
import helpers
from sklearn import metrics
from operator import itemgetter


def main():
    AUC('../generators/train.csv', '../generators/test.csv', '../mahout/testikus.txt')
    
    
def buildDictByIndex(X, index=0):
    
    d = dict()
    
    for x in X:
        if x[index] in d:
            d[x[index]].append(x)
        else:
            d[x[index]] = list()
            d[x[index]].append(x)
   
    return d  

def sortDictByRatings(predictions):
    
    for user in predictions:
        predictions[user] = sorted(predictions[user], key=itemgetter(2))
    return predictions
    

def AUC(train, test, pred):
    
    train = helpers.readRatingsFromFile(train)
    test_ratings = helpers.readRatingsFromFile(test)
    predicted_ratings = helpers.readRatingsFromFile(pred)[1:]
    
    train_users = buildDictByIndex(train, 0)
    test_users = buildDictByIndex(test_ratings, 0)
    predictions = buildDictByIndex(predicted_ratings, 0)
    
    sortDictByRatings(predictions)
    
    numCandidateItems = countUniqueItems(train)
    #print('Number of candidate items: %d' %numCandidateItems)
    
    AUC = 0
    num_users = 0

    for user in test_users:
        
        numCandidateItemsThisUser = numCandidateItems - len(train_users[user])
        #print('Number of ratings for this user: %d' %len(test_users[user]))
        print("Cand item Count:%d Ignore User:%d" %(numCandidateItems, len(train_users[user])))
        
        if user in predictions:
            predictionCount = len(predictions[user])
            numDroppedItems = numCandidateItemsThisUser - predictionCount
            print("Num cand user:%d Pred Count: %d" %(numCandidateItemsThisUser, predictionCount))
            AUC += areaUnderCurve(predictions[user], test_users[user], numDroppedItems)
            #AUC += AUCScikitLearn(predictions[user], test_users[user], numDroppedItems)
            num_users += 1
        else:
            predictionCount = 0
        
    print('AUC: %.2f' %(AUC/float(num_users)))
    return AUC/float(num_users)    

def countUniqueItems(ratings):
    
    items = []
    
    for rating in ratings:
        if rating[1] not in items:
            items.append(rating[1])
            
    return len(items)
        
def areaUnderCurve(predictionList, correctItems, numDroppedItems):
    
    numRelevantItems = 0    #Number of relevant items found in predictions
    
    #How many of the relevant items can be found in the users list?
    for testItem in correctItems:
        if any(x[1] == testItem[1] for x in predictionList):
            numRelevantItems += 1
    
    numEvalItems = len(predictionList) + numDroppedItems
    numEvalPairs = (numEvalItems - numRelevantItems) * numRelevantItems  
    
    print('Num relevant items: %d numEvalItems: %d numEvalPairs %d' %(numRelevantItems, numEvalItems, numEvalPairs))
    
    if numEvalPairs < 0:
        print('numEvalPairs cannot be less than 0')
        
    if numEvalPairs == 0:
        return 0.5
    
    numCorrectPairs = 0
    hitCount = 0
    for item in predictionList:
        if not any(x[1] == item[1] for x in correctItems):
            numCorrectPairs += hitCount
        else:
            hitCount += 1
    
    missingRelevantItems = len(correctItems) - numRelevantItems
    numCorrectPairs += hitCount * (numDroppedItems - missingRelevantItems)
    
    print('numCorrectPairs: %d missingRelevantItems %d hitCount %d' %(numCorrectPairs, missingRelevantItems, hitCount))
    
    
    AUC = numCorrectPairs / float(numEvalPairs)
    
    return AUC 

def AUCScikitLearn(predictionList, correctItems, numDroppedItems):
    
    item_ids = []
    
    for rating in correctItems:
        if not rating[1] in item_ids:
            item_ids.append(rating[1])
    
    for prediction in predictionList:
        if not prediction[1] in item_ids:
            item_ids.append(prediction[1]) 
            
    y = []
    pred = []
    
    for item in item_ids:
        if any(x[1] == item for x in correctItems):
            y.append(2)
        else:
            y.append(1)
        if any(x[1] == item for x in predictionList):
            pred.append(1)
        else:
            pred.append(0)
            
    
    fpr, tpr, thresholds = metrics.roc_curve(y, pred, pos_label=2)
    return metrics.auc(fpr, tpr)
     

if __name__ == "__main__":
    main()




