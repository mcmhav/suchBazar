'''
Filterbots: Sobazar

'''

from collections import Counter
from collections import OrderedDict
from operator import itemgetter
import datetime

import helpers
import csv
import random
import time
from multiprocessing import Process, Queue
import os

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)
GENERATED_LOCATION = 'generated'
SAVE_FOLDER = 'Data'
folder = ROOT_FOLDER + '/' + GENERATED_LOCATION + '/' + SAVE_FOLDER + '/'

if not os.path.exists(folder):
    os.makedirs(folder)

def filterOutOldRatings(ratings, num_weeks=4):
    '''
    Removes ratings given num_weeks before the last
    added rating.
    '''
    filteredRatings = []
    ratings = sorted(ratings, key=itemgetter(3), reverse=True)
    newest = datetime.datetime.fromtimestamp(ratings[0][3])
    limit = newest - datetime.timedelta(days=7*num_weeks)
    limit = int(limit.strftime('%s'))

    for rating in ratings:
        if rating[3] >= limit:
            filteredRatings.append(rating)
    #print('Filtered out %d old ratings' %(len(ratings)-len(filteredRatings)))
    return filteredRatings


def criticBot(ratings, num_critics=20, recentness=False):
    '''
    Select a set of critics among the most active users
    inject their average ratings directly into the user-item matrix
    '''
    start = time.time()
    #print('Generating criticBot Ratings...')

    criticBotId = 1339
    userRatings = {}
    itemCounter = Counter()
    itemRatings = Counter()
    criticBotRatings = []
    i = 0


    if recentness:
        ratings = filterOutOldRatings(ratings, 8)

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

    #print('criticBot used %d seconds to generate %d ratings' %(time.time()-start, len(criticBotRatings)))

    return criticBotRatings


def getBrand(itemid, item_attributes):
    '''
    Returns the brand id for a given item
    '''
    #return item_attrib.get(itemid, False)

    for item in item_attributes:
        if item[0] == itemid:
            return int(item[2])
    return 0

def brandBot(ratings, item_attributes):
    '''
    Inject average brand rating for each item
    '''
    start = time.time()
    #print('Generating brandBot Ratings...')

    brandBotId = 1337
    brandAverage = {}
    brandCounter = {}
    botRatings = []
    itemBrands = {}
    item_attributes = buildHashmap(item_attributes)
    uniqueItemsD = {}
    
    for rating in ratings:
        if not uniqueItemsD.get(rating[1], None):
            uniqueItemsD[rating[1]] = 1
        brand = getBrandHashmap(rating[1], item_attributes)
        if not brand in brandAverage:
            brandAverage[brand] = 0
        if not brand in brandCounter:
            brandCounter[brand] = 0
        brandAverage[brand] += float(rating[2])
        brandCounter[brand] += 1
    brandAverage.pop(0, None) #Remove items with no brand
    brandAverage = {k: float(brandAverage[k])/brandCounter[k] for k in brandAverage}
    
    for item in item_attributes: 
        if brandAverage.get(item_attributes[item], None):
            botRatings.append([brandBotId, item, brandAverage[item_attributes[item]]])

    #print('brandBot used %d seconds to generate %d ratings' %(time.time()-start, len(botRatings)))
    return botRatings


def getUniqueBrandList(item_attributes):

    brands = []
    for item in item_attributes:
        if not int(item[2]) in brands and int(item[2]) != 0:
            brands.append(int(item[2]))
    
    return brands

def getUniqueItemList(ratings):

    items = []
    for rating in ratings:
        if not rating[1] in items:
            items.append(rating[1])
    
    return items

def getBrandHashmap(item_id, item_attributes):

    return int(item_attributes.get(int(item_id), 0))

def buildHashmap(item_attributes):

    hashMap = {}

    for item in item_attributes:
        if not int(item[0]) in hashMap:
            hashMap[int(item[0])] = item[2]

    return hashMap

def rateItemsByBrand(items, item_attributes, userId, brandId):

    botRatings = []
    for itemid in items:
        brand = getBrandHashmap(itemid, item_attributes)
        if int(brand) == int(brandId):
            botRatings.append([userId, itemid, 5.0])

    #print(len(botRatings))
    return botRatings

def brandBots(ratings, item_attributes):
    '''
    Inject one filterbot user for each brand
    where each filterbot user gives each item of a specific
    brand a maximum rating
    '''

    start = time.time()
    #print('Generating multiple brand bots...')
    ratings = ratings[1:]
    botRatings = []
    brands = getUniqueBrandList(item_attributes)
    items = getUniqueItemList(ratings)
    item_attributes = buildHashmap(item_attributes)
    botIds = range(1200, 1200+len(brands))
    for x, y in zip(botIds, brands):
        botRatings.extend(rateItemsByBrand(items, item_attributes, x, y))
        #print('processed bot %d of %d ' % (len(botIds) -(max(botIds) - x), len(botIds)))

    #print('brandBotUsers used %d seconds to generate %d ratings' %(time.time()-start, len(botRatings)))
    return botRatings


def averageBot(ratings):
    '''
    Injects the average for each item over all users
    '''

    start = time.time()
    #print('Generating averageBot Ratings...')

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

    #print('averageBot used %d seconds to generate %d ratings' %(time.time()-start, len(averageItemRatings)))
    return averageItemRatings



def popularityBot(ratings, max_rating, rating_limit=3, recentness=False):

    '''
    Rates all items based on their popularity,
    u(i) = V_i * normalization factor that caps the rating at 5
    '''
    start = time.time()
    #print('Generating popularityBot Ratings...')

    if recentness:
        ratings = filterOutOldRatings(ratings,4)


    VTBotId = 1338
    itemCounter = Counter()
    VTBotRatings = []

    for rating in ratings:
        itemCounter[rating[1]] += 1

    mostPopularCount = itemCounter.most_common()[0][1]

    for key, value in itemCounter.most_common():

        if value > rating_limit:
            rating = (value/mostPopularCount)*(2)+3
            VTBotRatings.append([VTBotId, key, rating])

    #print('popularityBot used %d seconds to generate %d ratings' %(time.time()-start, len(VTBotRatings)))
    return VTBotRatings


def conformityBot(ratings, threshold=4.5):
    '''
    'Buys' items more than one other user also have bought
    '''

    start = time.time()
    #print('Generating conformityBot Ratings...')

    botId = 1334
    boughtCounter = Counter()
    botRatings = []

    for rating in ratings:
        if rating[2] > threshold:
            boughtCounter[rating[1]] += 1

    for item in boughtCounter:
        if boughtCounter[item] > 1:
            botRatings.append([botId, item, 5.0])

    #print('conformityBot used %d seconds to generate %d ratings' %(time.time()-start, len(botRatings)))
    return botRatings


def readRatings(path):
    ratings = []
    with open(path, 'r') as file:
        dialect = csv.Sniffer().sniff(file.read(1024))
        reader =  csv.reader(file, delimiter=dialect.delimiter)
        for rating in reader:
            #if len(rating) >= 3:
            #    if rating[0] != '' and rating[1] != '' and rating[2] != '':
            #       ratings.append([int(rating[0]), int(rating[1]), float(rating[2])])
            ratings.append(rating)
    return ratings

def writeRatingsToFile(fileName, data, delimiter=','):

    with open(folder + fileName, 'wb') as file:
        writer =  csv.writer(file, delimiter=delimiter)
        writer.writerows(data)

def readItemAttributes(path):
    itemAttributes = []
    #print (path)
    with open(path, 'r') as f:
        reader =  csv.reader(f, delimiter='\t')
        for item in reader:
            itemAttributes.append([int(item[0]), int(item[1]),int(item[2]),int(item[3]),int(item[4]),int(item[5]),int(item[6])])
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
        writeRatingsToFile('train.txt', train, '\t')
        writeRatingsToFile('test.txt', test, '\t')
    else:
        train = ratings

    train.extend(brandBot(train, item_attributes))
    train.extend(averageBot(train))
    train.extend(popularityBot(train, 5))
    #train.extend(criticBot(train))
    #train.extend(conformityBot(train))

    writeRatingsToFile('ftrain.txt', train, '\t')

def addFilterBotRatings(train, featurefile='', fbots=[0,0,0,0,0]):

    
    #item_attributes = readItemAttributes('/home/thomalm/python/suchBazar/generated/itemFeatures.txt')
    fbRatings = []
    #ratings = readRatings('/home/thomalm/python/suchBazar/generated/ratings/blend.txt')
    item_attributes = readItemAttributes(featurefile)
    
    if fbots[0]:
        fbRatings.extend(brandBot(train, item_attributes))
    if fbots[1]:
        fbRatings.extend(averageBot(train))
    if fbots[2]:
        fbRatings.extend(popularityBot(train, 5))
    if fbots[3]:
        fbRatings.extend(criticBot(train))
    if fbots[4]:
        fbRatings.extend(brandBots(train, item_attributes))
    
    
    '''
    procs = []
    q = Queue()

    if fbots[0]:
        p0 = Process(target=testur, args=[fbRatings, brandBot, train, item_attributes])
        p0.start()
        procs.append(p0)
    if fbots[1]:
        p1 = Process(target=testur, args=[fbRatings, averageBot, train])
        p1.start()
        procs.append(p1)
    if fbots[2]:
        p2 = Process(target=testur, args=[fbRatings, popularityBot, train, 5])
        p2.start()
        procs.append(p2)
    if fbots[3]:
        p3 = Process(target=testur, args=[fbRatings, criticBot, train])
        p3.start()
        procs.append(p3)
    if fbots[4]:
        p4 = Process(target=testur, args=[fbRatings, brandBots, train, item_attributes])
        p4.start()
        procs.append(p4)

    
    for p in procs:
        p.join()
    '''
    
    return train + fbRatings


def testur(fbRatings, bot, *args):
    '''
    '''
    
    fbRatings.extend(bot(*args))
  
    
    



### TESTING ###
#ratings = helpers.readRatingsFromFile('../generators/ratings/count_linear.txt', True)[1:]

### TESTING ###
#ratings = readRatings('../../datasets/blend.txt')
#ratings = readRatings('/home/thomalm/python/suchBazar/generated/ratings/blend.txt')
#item_attributes = readItemAttributes('/home/thomalm/python/suchBazar/generated/itemFeatures.txt')
#brandBot(ratings, item_attributes)
#brandBots(ratings, item_attributes)

#createSplit(ratings, item_attributes, 0.1)
#createSplit(ratings, item_attributes, 0.1, False)
#averageItemBot(ratings)
#popularityBot(ratings, 5, 10)
#VTBot(ratings, 5)



