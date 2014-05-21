'''
Filterbots: Sobazar

'''


from collections import Counter
from collections import OrderedDict

import csv
import random
import time

def criticBot(ratings, num_critics=20):
    '''
    Select a set of critics among the most active users
    inject their average ratings directly into the user-item matrix
    '''
    start = time.time()
    print('Generating criticBot Ratings...')
    
    criticBotId = 1339
    userRatings = {}
    itemCounter = Counter()
    itemRatings = Counter()
    criticBotRatings = []
    i = 0
    
    for rating in ratings:
        if not rating[0] in userRatings:
            userRatings[rating[0]] = list()
        userRatings[rating[0]].append(rating)    
        
    userRatings = OrderedDict(sorted(userRatings.viewitems(), key=lambda (k,v):len(v), reverse=True))  
    critics = random.sample(range(num_critics*2), num_critics)

    for user in userRatings:
        if i in critics:
            for item in userRatings[user]:
                itemRatings[item[1]] += item[2]
                itemCounter[item[1]] += 1
        i += 1
        if i > max(critics):
            break
        
    itemRatings = {k: float(itemRatings[k])/itemCounter[k] for k in itemRatings}       
        
    for item in itemRatings:
        criticBotRatings.append([criticBotId, item, itemRatings[item]])
        
    print('criticBot used %d seconds to generate %d ratings' %(time.time()-start, len(criticBotRatings)))
    
    return criticBotRatings
    

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
    start = time.time()
    print('Generating brandBot Ratings...')
    
    brandBotId = 1337
    brandAverage = {}
    brandCounter = {}
    botRatings = []
    itemBrands = {}
    uniqueItems = [] 
    
    for rating in ratings:
        if not rating[1] in uniqueItems:
            uniqueItems.append(rating[1])
        if rating[1] in itemBrands:
            brand = itemBrands[rating[1]]
        else:    
            brand = getBrand(rating[1], item_attributes)
            itemBrands[rating[1]] = brand
        if not brand in brandAverage:
            brandAverage[brand] = 0  
        if not brand in brandCounter:
            brandCounter[brand] = 0
        brandAverage[brand] += rating[2]
        brandCounter[brand] += 1
           
    brandAverage = {k: float(brandAverage[k])/brandCounter[k] for k in brandAverage}
        
    for item in item_attributes:
        if int(item[0]) in uniqueItems:
            botRatings.append([brandBotId, item[0], brandAverage[item[2]]])
            
    print('brandBot used %d seconds to generate %d ratings' %(time.time()-start, len(botRatings))) 
    return botRatings
    
def averageBot(ratings):
    '''
    Injects the average for each item over all users
    '''
    
    start = time.time()
    print('Generating averageBot Ratings...')
    
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
        
    print('averageBot used %d seconds to generate %d ratings' %(time.time()-start, len(averageItemRatings)))
    return averageItemRatings
           
    
def popularityBot(ratings, max_rating, rating_limit=10):
    '''
    Rates all items based on their popularity,
    u(i) = V_i * normalization factor that caps the rating at 5
    '''
    start = time.time()
    print('Generating popularityBot Ratings...')
    
    VTBotId = 1338
    itemCounter = Counter()
    VTBotRatings = []
    
    for rating in ratings:
        itemCounter[rating[1]] += 1
    
    mostPopularCount = itemCounter.most_common()[0][1]
        
    for key, value in itemCounter.most_common():
        if not value < rating_limit: 
            rating = (value/mostPopularCount)*(2)+3
            VTBotRatings.append([VTBotId, key, rating])
        
    print('popularityBot used %d seconds to generate %d ratings' %(time.time()-start, len(VTBotRatings)))
    return VTBotRatings


def conformityBot(ratings, threshold=4.5):
    '''
    'Buys' items more than one other user also have bought
    '''
    
    start = time.time()
    print('Generating conformityBot Ratings...')
    
    botId = 1334
    boughtCounter = Counter()
    botRatings = []
    
    for rating in ratings:
        if rating[2] > threshold:
            boughtCounter[rating[1]] += 1

    for item in boughtCounter:
        if boughtCounter[item] > 1:
            botRatings.append([botId, item, 5.0])
            
    print('conformityBot used %d seconds to generate %d ratings' %(time.time()-start, len(botRatings)))
    return botRatings

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
    
def writeRatingsToFile(path, data, delimiter=','):

    with open(path, 'wb') as file:
        writer =  csv.writer(file, delimiter=delimiter)
        writer.writerows(data)    

def readItemAttributes(path):
    
    itemAttributes = []
    
    with open(path, 'r') as file:
        reader =  csv.reader(file, delimiter='\t')
        for item in reader:
            itemAttributes.append(item)
            
    return itemAttributes
        
def createSplit(ratings, item_attributes, test_ratio, split=True):
    '''
    TODO: Do not extend an extended list...
    '''
    
    #If the supplied ratings are to be splitted in a test and tranining set
    if split:
        random.shuffle(ratings)
        numTestRatings = int(len(ratings)*test_ratio)
        test = ratings[:numTestRatings]
        train = ratings[numTestRatings:]
        #Write original 'unenhanced' training set to file
        writeRatingsToFile('./Data/train.txt', train, '\t')
        writeRatingsToFile('./Data/test.txt', test, '\t')
    else:
        train = ratings
    
    train.extend(brandBot(train, item_attributes))
    train.extend(averageBot(train))
    train.extend(popularityBot(train, 5))
    #train.extend(criticBot(train))
    #train.extend(conformityBot(train))
    
    writeRatingsToFile('./Data/ftrain.txt', train, '\t')
    
def addFilterBotRatings(train, fbots=[0,0,0,0,0]):
    
    item_attributes = readItemAttributes('../data/product_features.txt')
    fbRatings = []
    
    if fbots[0]:
        fbRatings.extend(brandBot(train, item_attributes))
    if fbots[1]:
        fbRatings.extend(averageBot(train))
    if fbots[2]:
        fbRatings.extend(popularityBot(train, 5))
    if fbots[3]:
        fbRatings.extend(criticBot(train))
    if fbots[4]:
        fbRatings.extend(conformityBot(train))
    
    return train + fbRatings 


### TESTING ###   
#ratings = readRatings('../../datasets/blend.txt')
#ratings = readRatings('Data/user_train3.txt')
#item_attributes = readItemAttributes('./Data/product_features.txt')
#createSplit(ratings, item_attributes, 0.1)
#createSplit(ratings, item_attributes, 0.1, False)
#brandBot(ratings, item_attributes)
#averageItemBot(ratings)
#VTBot(ratings, 5)


    