'''
Most Popular Recommender

'''

import csv
import json
import sys
from collections import Counter
import operator
#import pymongo
import random
import math

#client = pymongo.MongoClient()
#db = client.item_popularity


#Product name filter
productNameFilter = ['Free', 'Sexy', 'Giftcard', 'Offer', 'Test', 'NULL']
#Only accept activity originating from the following countries
countryFilter = ['Norway']
#Only accept the following event_ids
eventFilter = ['product_detail_clicked', 'product_wanted', 'product_purchase_intended', 'featured_product_clicked', 'product_purchased']

#Example weighting scheme for the different events
weighting = { 'product_detail_clicked': 1,
             'product_wanted': 3,
             'product_purchase_intended': 5,
             'featured_product_clicked': 1,
             'product_purchased': 1
             };

def validateRow(row):
    '''
    Data filter function
    Filter out the irrelevant data through multiple checks
    '''
    
    #Decode JSON object
    event_json = json.loads(row[31])
    eventData = json.loads(event_json['eventData'])

    #Stage 1: Filter out irrelevant events
    if not any(row[1] for s in eventFilter):
        return False

    #Stage 2: Filter out staging and test data
    #Hack for getting around some invalid lines in the dataset not containing they key serverEnvionrment
    try:
        if eventData['serverEnvironment'] != 'prod':
            return False
    except KeyError:
        return False
 
    #Stage 3: Filter by product name
    if any(s in row[29].split() for s in productNameFilter):
        return False

    #Stage 4: Filter by GPS coordinates / country
    if not any(row[25] for s in countryFilter):
        return False

    return True


def preProcessData():
    '''
    Process and filter the database dump and sort the items by popularity
    based on a predetermined weighting scheme for each activity
    '''

    popularityCounter = Counter()
    idToProductNameMapper = dict()

    print('Reading and filtering dataset...')

    with open('Data/sobazar.tab', 'r') as tsv:
        reader = csv.reader(tsv, delimiter='\t')   
        next(reader)
        for row in reader:
            #If row passes filtering            
            if validateRow(row):
                event_data = json.loads(row[2])
                popularityCounter[event_data['product_id']] += weighting[row[1]]
                idToProductNameMapper[event_data['product_id']] = event_data['product_name']


    popularityCounter = sorted(popularityCounter.items(), key=operator.itemgetter(1), reverse=True)

    print('Writing popularity data to file...')

    with open('Data/popularity.csv', 'wb') as file:
        file.write('product_id,product_name,popularity\n')
        for product_id, popularity in popularityCounter:
            file.write(product_id + ',' + idToProductNameMapper[product_id]  + ',' + str(popularity) + '\n')

    print('Done!')
    
def readPopularityData():
    '''
    Read the pre-processed popularity data from file
    '''

    data = []

    with open('Data/popularity.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            data.append(row)

        return data           
                  
def recommendItems(items, no_items, top_n):
    '''
    Recommend items using result dithering / permutation
    Returns the new top_n items
    '''
       
    #Alternative 1: Score = log(rank) - runif(x, y)
    list = [math.log(x+1, 2) - random.uniform(8, 2) for x in range(no_items)]    
    #Alternative 2: Score = log(rank) - 3.0*rexp(8)
    #list = [math.log(x+1, 2) - 3.0*random.expovariate(8) for x in range(no_items)]    
    
    list = sorted(range(len(list)), key=lambda x:list[x])
    #Print permutation 
    print (list[0:top_n])
    recommendations = [items[x] for x in list[0:top_n]]
    
    return recommendations
       
def generatePermuations(items, no_items, top_n):
    
    print('Alternative 1 permutations:')
    for i in range(10):
        list = [math.log(x+1, 2) - random.uniform(10, 2) for x in range(no_items)]
        list = sorted(range(len(list)), key=lambda x:list[x])
        print (list[0:top_n])
    
    print('Alternative 2 permutations:')
    for i in range(10):
        list = [math.log(x+1, 2) - 3.0*random.expovariate(2.5) for x in range(no_items)]
        list = sorted(range(len(list)), key=lambda x:list[x])
        print (list[0:top_n])  
           
def main():
    #preProcessData()
    items = readPopularityData()
    generatePermuations(items, 100, 10)
    #recommendations = recommendItems(items, 50, 15)
    #print (recommendations)     
     
if __name__ == '__main__':
    main()