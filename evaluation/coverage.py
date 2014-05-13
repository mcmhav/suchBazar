'''
Functions for measuring the user- and item-space coverage of a method

User-space coverage: Percentage of the users the method is able to generate at least one recommendation for
Item-space coverage: Percentage of the items that are recommendable

NB! When measuring Item-space coverage, set the number of items to recommend 'really' high
'''

import csv
import helpers
        
def countUniqueUsersAndItems(ratings):    
    
    users = []
    items = []

    for rating in ratings:
        users.append(rating[0])
        items.append(rating[1])
    
    users = set(users)
    items = set(items)
    return len(users), len(items)   
    
def measureCoverage(train, predictions):
      
    #ratings = readRatingsFromFile('../generators/ratings/naive.txt' ,'\t')
    #predicted_ratings = readRatingsFromFile('../mahout/testikus.txt')
    
    u, i = countUniqueUsersAndItems(train)
    u_p, i_p = countUniqueUsersAndItems(predictions)

    userSpaceCoverage = u_p/float(u)
    itemSpaceCoverage = i_p/float(i)
    
    #print('User-space coverage: %.2f' %(userSpaceCoverage))
    #print('Item-space coverage: %.2f' %(itemSpaceCoverage))

    return userSpaceCoverage, itemSpaceCoverage
        
    



