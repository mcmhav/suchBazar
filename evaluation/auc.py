import helpers

def compute(train, test, predictions):
    '''
    Computes the AUC for all users in the test set
    For more information about AUC see e.g.
    https://www.kaggle.com/wiki/AreaUnderCurve
    For Java implementation see:
    https://github.com/jcnewell/MyMediaLiteJava/blob/master/src/org/mymedialite/eval/Items.java
    '''

    train_users = helpers.buildDictByIndex(train, 0)
    test_users = helpers.buildDictByIndex(test, 0)
    predictions = helpers.buildDictByIndex(predictions, 0)
    #sortDictByRatings(predictions)                                #The ratings usually comes pre sorted

    candidateItems = helpers.getUniqueItemList(train)

    numCandidateItems = len(candidateItems)                       #Number of unique items in training set

    AUC = 0
    num_users = 0

    for user in test_users:

        #Number of items that are recommendable to the user (all items - those already rated)
        numCandidateItemsThisUser = numCandidateItems
        if user in train_users:
            numCandidateItemsThisUser -= len(train_users[user])

        if user in predictions:                                   #Check if user is in the prediction set
            predictionCount = len(predictions[user])              #Length of the users prediction set
            #if predictionCount < numCandidateItemsThisUser:
                #TODO - Consider adding a function for randomly appending the missing items
                # print('Warning: Not all items have been ranked!')
            numDroppedItems = numCandidateItemsThisUser - predictionCount
            AUC += auc(predictions[user], test_users[user], numDroppedItems)
            num_users += 1

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




