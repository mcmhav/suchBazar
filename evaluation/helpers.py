import sys
import json
import pymongo
import csv
import re
from datetime import datetime
import time
from operator import itemgetter
import os
import sys
import traceback
f = ""

def main():
    '''
    Helper functions
    '''

def prepareEvauationScoreToLaTeX(filename,us_coverage,is_coverage,auc,mapk,eStats,k):
    '''
    Make latex structure
    AUC - MAP - T_c - T_w - T_p - P_c - P_w - P_p - R_c - R_w - R_p - MAP_c - MAP_w - MAP_p - IS_c - IS_c
    '''

    SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
    ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)
    GENERATED_LOCATION = 'generated'
    SAVE_FOLDER = 'evaluationScore'
    folder = ROOT_FOLDER + '/' + GENERATED_LOCATION + '/' + SAVE_FOLDER + '/'

    if not os.path.exists(folder):
        os.makedirs(folder)

    saveName = folder + k  + "-" + filename + ".score"
    print(eStats)
    f = open(saveName, 'w')
    f.write('01auc:' + auc + "\n")
    f.write('02map:' + mapk + "\n")
    f.write('03T_c:' + str(eStats[0]) + "\n")
    f.write('04T_w:' + str(eStats[1]) + "\n")
    f.write('05T_p:' + str(eStats[2]) + "\n")
    f.write('06P_c:' + str(eStats[3]) + "\n")
    f.write('07P_w:' + str(eStats[4]) + "\n")
    f.write('08P_p:' + str(eStats[5]) + "\n")
    f.write('09R_c:' + str(eStats[6]) + "\n")
    f.write('10R_w:' + str(eStats[7]) + "\n")
    f.write('11R_p:' + str(eStats[8]) + "\n")
    f.write('12MAP_c:' + str(eStats[9]) + "\n")
    f.write('13MAP_w:' + str(eStats[10]) + "\n")
    f.write('14MAP_p:' + str(eStats[11]) + "\n")
    f.write('15us_coverage:' + us_coverage + "\n")
    f.write('16is_coverage:' + is_coverage + "\n")
    f.write('k:' + k + "\n")
    f.close()

    print ("wrote to %s" % saveName)

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
    f.close()
    for line in lines:
        tmp = line.split(',')
        predictions.append([int(tmp[0]), int(tmp[1]), float(tmp[2])])
    return predictions

def closeF():
    global f
    f.close()

def readRatingsFromFile(path, convert=False):
    ratings = []
    if not os.path.isfile(path):
      sys.stderr.write("File %s does not exist\n" % (path))
      sys.exit(1)
    f = open(path, 'r+')
    lines = f.readlines()
    f.close()
    for line in lines:
        l = line.split('\t')

        # Parse the components in rating file.
        user_id = l[0].strip()
        product_id = l[1].strip()
        rating = l[2].strip()
        timestamp = l[3].strip() if len(l) > 3 else None

        # Dont do anything if any of these are not there.
        if not user_id or not product_id or not rating:
          continue

        # These are always included.
        r = [int(user_id), int(product_id), float(rating)]

        # Add timestamp, and convert to unix-time if asked for.
        if timestamp:
          if convert:
            t = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            timestamp = int(time.mktime(t.timetuple()))
          r.append(timestamp)

        # Add all the stuff to ratings array.
        ratings.append(r)
    return ratings

def readRatingsFromFileSmart(path, convert=False):
    ratings = []
    with open(path, 'r') as file:

        dialect = csv.Sniffer().sniff(file.read(1024))
        reader =  csv.reader(file, delimiter=dialect.delimiter)

        for rating in reader:
            try:
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
            except:
                print (rating)
                print ("readRatingsFromFileSmart")
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
            if not s[1]:
                continue
            items = s[1].split(',')
            for item in items:
                i = item.split(':')
                try:
                    userID = int(s[0])
                    itemID = int(i[0])
                    rating = float(i[1])
                    ratingTriple = [userID, itemID, rating]
                    ratings.append(ratingTriple)
                except:
                    print (item)
                    print (line)
                    print ('wtf')
                    sys.exit()
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

def writeRatingsToFile(path, data, delimiter='\t'):

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

    d = {}
    for x in X:
        try:
            if isinstance(x,list):
                i = int(x[index])
                if not i in d:
                    d[i] = list()
                d[i].append(x)
        except:
            print (x)
            print ("buildDictByIndex error")
            sys.exit()
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

def preprocessMAP(a, p, k):
    '''
    Preprocessing nMAP calculations
    Extracts the top k list of item-ids from each user
    '''

    pred = []
    test = []

    for user in a:
        utest = []
        for i in range(len(a[user])):
            utest.append(a[user][i][1])
        if user in p:
            upred = []
            #p[user] = sorted(p[user], key=itemgetter(2), reverse=True)
            for j in range(min(len(p[user]), k)):
                upred.append(p[user][j][1])
            test.append(utest)
            pred.append(upred)
    print(len(test), len(pred))
    return test, pred

def preprocessMeanAvgPrecision(events, predicted, k):

    test = []
    predictions = []

    for user, user_pred_ratings in predicted.iteritems():
        #predictions.append(user_ratings)
        user_test_items = []
        user_pred_items = []

        for rating in events:
            if rating[0] == user:
                user_test_items.append(rating[1])

        #If the user is in the test set
        if len(user_test_items) > 0:

            for rating in user_pred_ratings[:min(len(user_pred_ratings), k)]:
                user_pred_items.append(rating[1])

            test.append(user_test_items)
            predictions.append(user_pred_items)

    return test, predictions

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
    return -1


if __name__ == "__main__":
    main()
    #print(determineLatexHeaderNumber('../data/itemtrain1'))



