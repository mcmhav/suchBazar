'''
Filterbots: Sobazar

'''


from collections import Counter

import csv

def criticBot(ratings):
    '''
    Select a set of critics that have rated more than x items (e.g. 10)
    inject their ratings directly into the user-item matrix
    '''
    

def getBrand(itemid, item_attributes):
    '''
    Returns the brand id for a given item
    '''
    for item in item_attributes:
        if int(item[0]) == itemid:
            return item[2]
    
    return 0

def brandBot(ratings, item_attributes):
    '''
    Inject average brand rating for each item
    '''
    brandBotId = 1337
    brandAverage = {}
    brandCounter = {}
    botRatings = []
    
    for rating in ratings:
        
        brand = getBrand(rating[1], item_attributes)
        if not brand in brandAverage:
            brandAverage[brand] = 0  
        if not brand in brandCounter:
            brandCounter[brand] = 0
        brandAverage[brand] += rating[2]
        brandCounter[brand] += 1
           
    brandAverage = {k: float(brandAverage[k])/brandCounter[k] for k in brandAverage}
        
    for item in item_attributes:
        botRatings.append([brandBotId, item[0], brandAverage[item[2]]])
            
    return botRatings
    
def averageItemBot(ratings):
    '''
    Injects the average for each item over all users
    '''
    
    averageItemBotId = 1336
    itemAverage = {}
    itemCounter = {}
    averageItemRatings = []
    
    for rating in ratings:
        if not rating[1] in itemAverage:
            itemAverage[rating[1]] = 0
        if not rating[1] in itemCounter:
            itemCounter[rating[1]] = 0
        itemAverage[rating[1]] += rating[2]
        itemCounter[rating[1]] += 1
    
    itemAverage = {k: float(itemAverage[k])/itemCounter[k] for k in itemAverage}
    
    for item in itemAverage:
        averageItemRatings.append([averageItemBotId, item, itemAverage[item]])
        
    return averageItemRatings
           
    
def VTBot(ratings):
    '''
    Rates all items based on their popularity,
    u(i) = V_i * normalization factor that caps the rating at 5
    '''


def costBot(ratings):
    '''
    Rate all cheap items highly?
    Rate all expensive items highly?
    '''


def windowshoppingBot(ratings):
    '''
    '''
    
    
def shopaholicBot(ratings):
    '''
    '''
    
def readRatings(path):
    ratings = []
    with open(path, 'r') as file:
        dialect = csv.Sniffer().sniff(file.read(1024))
        reader =  csv.reader(file, delimiter=dialect.delimiter)
        for rating in reader:
            if len(rating) >= 3:
                if rating[0] != '' and rating[1] != '' and rating[2] != '':
                    ratings.append([int(rating[0]), int(rating[1]), float(rating[2])])
    return ratings
    
def readItemAttributes(path):
    
    itemAttributes = []
    
    with open(path, 'r') as file:
        reader =  csv.reader(file, delimiter='\t')
        for item in reader:
            itemAttributes.append(item)
            
    return itemAttributes
        

   
ratings = readRatings('../../datasets/blend.txt')
item_attributes = readItemAttributes('./Data/product_features.txt')
#brandBot(ratings, item_attributes)
averageItemBot(ratings)
    