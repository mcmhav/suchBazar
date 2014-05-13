import helpers
import numpy as np


def main():
    '''
    '''

def compute(test, predictions, beta):
    '''
    Half life utility
    Scores a prediction based on the order of the items.
    "beta" is used to decide how much weight to be given to items
    further down the list.
    With high "beta" items down the list will be negligible
    '''

    test_users = helpers.buildDictByIndex(test, 0)
    predictions = helpers.buildDictByIndex(predictions, 0)

    HLU = 0
    HLUMax = 0
    num_users = 0

    for user in test_users:
        if user in predictions:
            HLU += hluU(test_users[user], predictions[user], beta)
            HLUMax += hluUMax()
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
        if p in actual:
            score += 1/(2**((j-1)*(beta-1)))
    return score

if __name__ == "__main__":
    main()
