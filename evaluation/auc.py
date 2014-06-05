import helpers
import random
import traceback
import sys

def appendZeroRatings(train, predictions, itemIds):
    '''
    Complete the prediction lists in order
    to successfully compute the AUC
    TODO - Do not include item ids in the users training set
    '''
    print('Appending missing items...')
    #Randomize the order missing items are added
    random.shuffle(itemIds)
    count = 0
    keyError = 0

    if len(train) == len(predictions):
        return predictions

    for user in predictions:
        for item in itemIds:
            try:
                if not any(x[1] == item for x in predictions[user]) and not any(y[1] == item for y in train[user]):
                    count += 1
                    predictions[user].append([user, item, 0.0])
            except Exception:
                #print('Key Error')
                keyError += 1
    print(keyError)
    print('Done appending %d missing items' % count)
    return predictions

def compute(train_users, test_users, predictions, candidateItems):
    '''
    Computes the AUC for all users in the test set
    For more information about AUC see e.g.
    https://www.kaggle.com/wiki/AreaUnderCurve
    For Java implementation see:
    https://github.com/jcnewell/MyMediaLiteJava/blob/master/src/org/mymedialite/eval/Items.java
    '''
        
    numCandidateItems = len(candidateItems)                       #Number of unique items in training set

    AUC = 0
    num_users = 0
    nonRankedItems = 0
    for user in test_users:

        #Number of items that are recommendable to the user (all items - those already rated)
        numCandidateItemsThisUser = numCandidateItems
        if user in train_users:
            numCandidateItemsThisUser -= len(train_users[user])

        if user in predictions:                                   #Check if user is in the prediction set
            predictionCount = len(predictions[user])              #Length of the users prediction set
            if predictionCount < numCandidateItemsThisUser:
                #TODO - Consider adding a function for randomly appending the missing items
                nonRankedItems += 1
            numDroppedItems = numCandidateItemsThisUser - predictionCount
            AUC += auc(predictions[user], test_users[user], numDroppedItems)
            num_users += 1

    #if nonRankedItems > 0:
        #print ('Warning: %s items have been ranked!' % nonRankedItems)
    if (float(num_users) == 0):
        print ("Error: Zero Test Users")
        return -1
    return AUC/float(num_users)

def auc(predictionList, correctItems, numDroppedItems):
    '''
    Compute the area under the ROC curve (AUC) of a list of ranked items.
    For java implementation see:
    https://github.com/jcnewell/MyMediaLiteJava/blob/master/src/org/mymedialite/eval/measures/AUC.java
    '''

    numRelevantItems = 0

    for testItem in correctItems:
        if any(x[1] == testItem[1] for x in predictionList):
            numRelevantItems += 1

    numEvalItems = len(predictionList) + numDroppedItems
    numEvalPairs = (numEvalItems - numRelevantItems) * numRelevantItems

    if numEvalPairs < 0:
        print('Correct items cannot be larger than Ranked Items')

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

    return numCorrectPairs / float(numEvalPairs)


def main():
    '''
    '''
    #How to run:
    #compute('../generators/train.csv', '../generators/test.csv', '../mahout/testikus.txt')

if __name__ == "__main__":
    main()




