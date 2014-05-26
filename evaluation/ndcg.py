import math

normalizationFactor = 5

def compute(actual, predicted, method, k):
    '''


    '''

    n_DCG = 0
    count = 0

    for actual, predicted in zip(actual, predicted):
        n_DCG += nDCG(actual[:k], predicted[:k], method)
        count += 1

    if (count == 0):
        return -1

    return n_DCG/float(count)


def nDCG(actual, predicted, method=0):
    '''
    Calculates nDCG for two lists

        actual: The State-of-the-Art or best possible ranking
        predicted: The ranking from the recommender

        The relevance of an item is assigned by taking 1/log(i+2),
        when iterating from 0

    '''

    rel = []    #Relevance Values
    DCG = 0     #Actual score
    IDCG = 0    #Best possible score

    for i in range(len(actual)):
        rel_i = relevance(i, actual[i][1], 1)
        rel.append([actual[i][0], rel_i]) #rel_{i} / log2(i)
        if method:
            IDCG += math.pow(2, rel_i)/math.log(i+2,2)
        else:
            IDCG += rel_i/math.log(2+i,2)

    for i in range(len(predicted)):
        for j in rel:
            if predicted[i][0] == j[0]:
                if method:
                    DCG += math.pow(2, j[1])/math.log(i+2,2)
                else:
                    DCG += j[1]/math.log(i+2,2)
    return DCG/IDCG

def relevance(i, r, method=0):
    '''
    Relevance functions
    '''
    if not method:
        return 1/math.log(2+i,2)
    else:
        return r/normalizationFactor

#TESTS
#test = [[1, 5], [2, 3.8], [3, 3.55], [4, 2.78], [5, 1.98]]
#pred = [[5, 0], [4, 0], [3, 0], [66, 0], [55, 0]]
#print(nDCG(test, pred, 1))

#test = [[[1, 5], [2, 3.8], [3, 3.55], [4, 2.78], [11, 1.98]], [[13, 5], [15, 3.8], [18, 3.55], [19, 2.78], [22, 1.98]]]
#pred = [[[1, 5], [2, 3.8], [3, 3.55], [4, 2.78], [11, 1.98]], [[13, 5], [15, 3.8], [122, 3.55], [19, 2.78], [212, 1.98]]]
#print(compute(test, pred, 1, 20))
