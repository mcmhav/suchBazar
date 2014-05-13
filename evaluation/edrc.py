# In order to deal with partial orders, the Expected Discounted Rank Correla-
# tion (EDRC) introduced by Ackerman and Chen, combines AP correlation with
# nDCG to measure the similarity between two sets of pairwise preferences. Similar
# to both of them, EDRC emphasizes preserving the order of the users most preferred
# items and applying a penalty for less preferred items. This metric tries to solve an
# important evaluation issue, that has been well introduced but not yet tested.

import math
from operator import itemgetter

def orderListByRating(ratings):
    '''
    Orders a list of ratings of the form <userid, itemid, rating>
    '''
    return sorted(ratings, key=itemgetter(2))
    

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
        rel_i = 1/math.log(2+i,2)
        rel.append([actual[i], rel_i]) #rel_{i} / log2(i)
        if method==0:
            IDCG += math.pow(2, rel_i)/math.log(i+2,2)
        else:
            IDCG += rel_i/math.log(2+i,2)
        
    for i in range(len(predicted)):
        for j in rel:
            if predicted[i] == j[0]:
                if method==0:
                    DCG += math.pow(2, j[1])/math.log(i+2,2)
                else:
                    DCG += j[1]/math.log(i+2,2)
                
                       
    return DCG/IDCG

def APCorrelation(actual, predicted):
    '''
    '''
       
   
    
def C(actual, predicted, index):
    '''
    Finds the number of items at an index less than index(i) that are correctly ranked
    according to the ground truth (actual)
    '''
    
def expectedDiscountedRankCorrelation(actual, predicted):
    '''
    EDRC
    '''
        
def setRanks(actual):
    '''
    Setting a rank
    '''
    

#Test
"""
actual = [[1,1],[1,2],[1,5],[1,4],[1,6],[1,7]]
predicted = [[1,1],[1,2],[1,5],[1,4],[1,6],[1,9]]
actual_2 = [[1,1],[1,2],[1,5],[1,4],[1,6],[1,7]]
predicted_2 = [[1,7],[1,5],[1,1],[1,2],[1,6],[1,9]]

print (nDCG(actual, predicted, 0))

assert nDCG(actual, predicted, 0) > nDCG(actual_2, predicted_2, 0)
assert nDCG(actual, predicted, 1) > nDCG(actual_2, predicted_2, 1)
"""
