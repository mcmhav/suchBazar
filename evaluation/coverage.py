'''

Functions for measuring the coverage of a recommender

Item-space Coverage: Percentage of all items that are
recommended (found in the prediction set)
User-space Coverage: Proportion of users the recommender
can recommend items to.


'''
        
def countUniqueUsersAndItems(ratings):
    '''
    Count unique users and items from a set
    of ratings on the form: <userid><itemid><rating>
    '''    

    users = []
    items = []

    for rating in ratings:
        users.append(rating[0])
        items.append(rating[1])
    
    users = set(users)
    items = set(items)
    return len(users), len(items)   
    
def compute(train, predictions):
    '''
    Computes both the user- and item-space coverage    '''
      
    predictions = removeZeroRatings(predictions)
    
    u, i = countUniqueUsersAndItems(train)
    u_p, i_p = countUniqueUsersAndItems(predictions)

    userSpaceCoverage = u_p/float(u)
    itemSpaceCoverage = i_p/float(i)

    return userSpaceCoverage, itemSpaceCoverage
        
def removeZeroRatings(predictions):
    '''
    Removes all 0.0 ratings from the prediction set
    TODO: Consider using a cutoff point, consider all ratings
    below a certain threshold as 0.0 ratings.
    '''
    
    nonZeroRatings = []
    
    for prediction in predictions:
        if prediction[2] != 0.0:
            nonZeroRatings.append(prediction)
            
            
    return nonZeroRatings
