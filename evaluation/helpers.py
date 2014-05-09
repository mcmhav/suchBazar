import sys
import json
import pymongo
import csv

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
    
def readRatingsFromFile(path):
    
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

if __name__ == "__main__":
    main()

