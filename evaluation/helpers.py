import sys
import json
import pymongo
import csv
from datetime import datetime
import time
from operator import itemgetter

f = ""

def main():
    '''
    Helper functions
    '''

def printProgress(count,total):
    progress = (count/total)*100
    sys.stdout.write("Progress: %s%%\r" % progress)
    sys.stdout.flush()

def is_json(myjson):
    try:
        json.loads(myjson)
    except (ValueError):
        return False
    return True

def getCollection(name,clean=False):
    client = pymongo.MongoClient()
    db = client.mydb
    col = db[name]
    if clean:
        col.remove()
    return col

def getCSVWriter(cFile):
    global f
    if sys.version_info >= (3,0,0):
        f = open(cFile + '.csv', "w", newline='')
    else:
        f = open(cFile + '.csv', "wb")
    return csv.writer(f)

def closeF():
    global f
    f.close()

def readRatingsFromFile(path, convert=False):

    ratings = []
    with open(path, 'r') as file:
        
        dialect = csv.Sniffer().sniff(file.read(1024))
        reader =  csv.reader(file, delimiter=dialect.delimiter)
        for rating in reader:
            if len(rating) == 3:
                if rating[0] != '' and rating[1] != '' and rating[2] != '':
                    ratings.append([int(rating[0]), int(rating[1]), float(rating[2])])
            if len(rating) > 3:
                if rating[0] != '' and rating[1] != '' and rating[2] != '' and rating[3] != '':
                    if convert:
                        t = datetime.strptime(rating[3],"%Y-%m-%d %H:%M:%S")
                        ratings.append([int(rating[0]), int(rating[1]), float(rating[2]), int(time.mktime(t.timetuple()))])
                    else:
                        ratings.append([int(rating[0]), int(rating[1]), float(rating[2]), int(rating[3])])           
    return ratings

def readRatings(path, timestamps):
    
    ratings = []
    with open(path, 'r') as file:
        
        lines = file.readlines()
        for line in lines:
            s = line.split('\t')
            ratings.append([int(s[0]), int(s[1]), float(s[2]), int(s[3])])
    return ratings

def readMyMediaLitePredictions(path):
    '''
    Prediction format:
    userid    [<itemid>:rating, ...<itemid>:rating]
    '''
    ratings = []
    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            s = line.split()
            s[1] = s[1].replace('[', '')
            s[1] = s[1].replace(']', '')
            items = s[1].split(',')
            for item in items:
                i = item.split(':')
                rating = [int(s[0]), int(i[0]), float(i[1])]
                ratings.append(rating)

    return ratings

def sortDictByRatings(predictions):
    '''
    Sorts a the ratings for each user (key)
    in descending order
    '''
    for user in predictions:
        predictions[user] = sorted(predictions[user], key=itemgetter(2), reverse=True)
    return predictions

def writeRatingsToFile(path, data, delimiter=','):

    with open(path, 'wb') as file:
        writer =  csv.writer(file, delimiter=delimiter)
        writer.writerows(data)

def countUniqueListEntities(ratings, index=0):
    '''
    Count the number of unique users (index=0),
    or items (index=1) from a list of ratings
    '''

    items = []

    for rating in ratings:
        if rating[index] not in items:
            items.append(rating[index])

    return len(items)

def buildDictByIndex(X, index=0):
    '''
    Builds a dictionary of from ratings
    index = 0, uses users as keys,
    index = 1, uses items as keys
    '''

    d = dict()

    for x in X:
        if x[index] in d:
            d[x[index]].append(x)
        else:
            d[x[index]] = list()
            d[x[index]].append(x)

    return d

def getUniqueItemList(ratings):

    uniqueItems = []
    for rating in ratings:
        if not rating[1] in uniqueItems:
            uniqueItems.append(rating[1])
    return uniqueItems

'''
def appendZeroRatings(user, predictions, candidateItems):
    for item in candidateItems:
        if not any(x[1] == item for x in predictions):
            predictions.append([user,item, 0.0])
    return predictions
'''

if __name__ == "__main__":
    main()

