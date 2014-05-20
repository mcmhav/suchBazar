import helpers
import numpy as np


def main():
    '''
    '''

    # train = helpers.readRatingsFromFile('../generators/ratings/no1.train')
    # test = helpers.readRatingsFromFile('../generators/ratings/no1.validate')
    # predictions = helpers.readRatingsFromFile('../generators/ratings/no1.predictions')
    # hlu = compute(test, predictions,2)
    # print (hlu)


def compute(actual, predicted, beta,k=100):
    '''
    Half life utility
    Scores a prediction based on the order of the items.
    "beta" is used to decide how much weight to be given to items
    further down the list.
    With high "beta" items down the list will be negligible (don't effect the score)
    '''

    # test_users = helpers.buildDictByIndex(test, 0)
    # predictions = helpers.buildDictByIndex(predictions, 0)

    HLU = 0
    HLUMax = 0
    num_users = 0

    for actual, predicted in zip(actual, predicted):
        tmpActual = actual[:k]
        tmpPredicted = predicted[:k]

        HLU += hluU(tmpActual, tmpPredicted, beta)
        HLUMax += hluUMax(tmpActual, beta)

        num_users += 1

    if HLUMax == 0:
        return -1
    return 100*(HLU/HLUMax)

def hluUMax(actual,beta):
    return hluU(actual,actual,beta)

def hluU(actual,predicted,beta):
    score = 0.0
    num_hits = 0.0

    for j,p in enumerate(predicted):
        for i,o in enumerate(actual):
            if p[0] == o[0]:
                score += 1/(2**((j-1)*(beta-1)))
    return score

if __name__ == "__main__":
    main()


