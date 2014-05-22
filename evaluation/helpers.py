import sys
import json
import pymongo
import csv
import re
from datetime import datetime
import time
from operator import itemgetter

f = ""

def main():
    '''
    Helper functions
    '''

def writeEvauationScoreToLaTeX(auc,map,ndcg,hlu):
    '''
    '''
    split_scores = scores.split('')

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

def readPredictionsFromFile(path):
    predictions = []
    f = open(path, 'r+')
    lines = f.readlines()
    for line in lines:
        tmp = line.split(',')
        predictions.append([int(tmp[0]), int(tmp[1]), float(tmp[2])])
    f.close()
    return predictions

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
                    tmp_rating = float(rating[2])
                    ratings.append([int(rating[0]), int(rating[1]), tmp_rating])
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
            if len(s) > 3:
                ratings.append([int(s[0]), int(s[1]), float(s[2]), int(s[3])])
            else:
                ratings.append([int(s[0]), int(s[1]), float(s[2])])
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

def readMyMediaLitePredictionsForMPR(path):
    '''
    Prediction format:
    userid    [<itemid>:rating, ...<itemid>:rating]
    Store in that format
    '''
    ratings = {}

    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            s = line.split()
            s[1] = s[1].replace('[', '')
            s[1] = s[1].replace(']', '')
            items = s[1].split(',')
            userRatings = {}
            for item in items:
                i = item.split(':')
                userRatings[int(i[0])] = float(i[1])
            ratings[int(s[0])] = userRatings

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

def preprocessMAP(actual, predictions, k):
    '''
    Preprocessing nMAP calculations

    Extracts the top k list of item-ids from each user

    '''

    a = buildDictByIndex(actual, 0)
    p = buildDictByIndex(predictions, 0)
    pred = []
    test = []
    for user in a:
        utest = []
        for i in range(len(a[user])):
            utest.append(a[user][i][1])
        test.append(utest)
        if user in p:
            upred = []
            p[user] = sorted(p[user], key=itemgetter(2), reverse=True)
            for j in range(k):
                upred.append(p[user][j][1])
            pred.append(upred)
    return test, pred

def preprocessDCG(actual, predictions, k):
    '''
    Preprocessing nDCG calculations

    Extracts the top k list of item-ids from each user

    '''

    a = buildDictByIndex(actual, 0)
    p = buildDictByIndex(predictions, 0)
    pred = []
    test = []
    for user in a:
        utest = []
        for i in range(len(a[user])):
            utest.append([a[user][i][1], a[user][i][2]])
        test.append(utest)
        if user in p:
            upred = []
            p[user] = sorted(p[user], key=itemgetter(2), reverse=False)
            for j in range(k):
                upred.append([p[user][j][1], p[user][j][2]])
            pred.append(upred)
    return test, pred

def determineLatexHeaderNumber(trainFile):
    
    #-1 in case the original rating file contains numbers
    split_num = int(re.findall(r'\d', trainFile)[-1])
    
    if 'system' in trainFile:
        if split_num == 1:
            return 40
        elif split_num == 2:
            return 60
        else:
            return 80
    else:
        if split_num == 1:
            return 10
        elif split_num == 2:
            return 40
        else:
            return 75
    

if __name__ == "__main__":
    main()
    print(determineLatexHeaderNumber('../data/itemtrain1'))
    


