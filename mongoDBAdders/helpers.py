import sys
import json
import pymongo
import csv

f = ""

def main():
    '''
    Helper functions
    '''

def get_without_neg_multipliers():
  return {
    'featured_product_clicked': [10,60],
    'product_detail_clicked': [10,60],
    'product_wanted': [60,80],
    'product_purchase_intended': [80,100],
    'product_purchased': [80,100]
  }

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

if __name__ == "__main__":
    main()

