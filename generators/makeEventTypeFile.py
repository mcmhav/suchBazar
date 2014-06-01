'''
Functions for making a eventType file to be used during evaluation
Generates a file on the form:
<Item ID><User ID><Event Type>
Product_detail_clicked is translated into 1
Product_wanted is translated into 2
Product_purchase_intended is translated into 3
'''

import csv
import json
import argparse
import os

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)

def createEventTypeFile(ratingFile, sobazarData):
    '''
    Generates a file on the form
    Item ID : Event Type
    To be used in evaluation
    ratings: path of rating file
    sobazarData: path of sobazar log file
    '''
    
    eventData = []

    with open(sobazarData, 'r') as tsv:
        reader = csv.reader(tsv, delimiter='\t')   
        #next(reader) #Skip Header
        for row in reader: 
            eventId = translateEvent(row[1])
            if eventId and row[12] != 'NULL':
                eventData.append([row[12], row[16], eventId])

    eventData = mergeList(eventData)
    eventData = cleanList(eventData, ratingFile)

    print('Writing event type data to file...')
    writeToFile(eventData)
    
def getUniqueItemList(ratings):
    '''
    *** Testing ***
    Get a list of all the unique Item IDs
    '''
    
    items = []
    
    for rating in ratings:
        items.append(rating[1])
        
    return set(items)  
    
def cleanList(eventData, ratingFile):
    '''
    *** Testing ***
    Remove items not in the rating file
    '''
    
    new_list = []
    
    ratings = readRatings(ratingFile)
    uniqueItems = getUniqueItemList(ratings)
    
    for event in eventData:
        if event[1] in uniqueItems:
            new_list.append(event)
      
    print('Removed %d items from the event list %d items remaining' %(len(eventData) - len(new_list), len(new_list)))        
            
    return new_list       
    
def mergeList(eventData):
    '''
    Merge the eventData list
    Items with multiple events are merged into one
    event with the most valuable event translation value
    '''    
    
    new_list = []
    
    
    users = {}
    
    for event in eventData:
        if not event[1] in users:
            users[event[1]] = list()
        users[event[1]].append(event)
        
    for user in users:
        events = {}  
        for event in users[user]:
            if not event[0] in events:
                events[event[0]] = list()
            events[event[0]].append(event)  
        for event in events:
            m = 0
            for i in range(len(events[event])):
                if events[event][i][2] > m:
                    m = events[event][i][2]
            new_list.append([user, events[event][0][0], m])     
    
    return new_list           
    
       
def translateEvent(eventType):
    '''
    Translate the event type if an object into an integer
    '''
    
    if eventType in ['product_detail_clicked', 'content:interact:product_detail_viewed', 'content:interact:product_clicked', 'content:interact:productClicked']:
        return 1
    if eventType in ['product_wanted', 'content:interact:product_wanted', 'content:interact:productWanted']:
        return 2
    if eventType in ['product_purchase_intended' or 'purchase:buy_clicked']:
        return 3
    return 0    

def readRatings(ratingFile):
    
    ratings = []
    
    with open(ratingFile, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            ratings.append(row)
          
    return ratings
    
def writeToFile(data):
    '''
    TODO: Move to utils.py or use file in utils.py?
    '''
    
    with open('../generated/event_type.txt', 'wb') as file:
        writer =  csv.writer(file, delimiter='\t')
        writer.writerows(data)
        

parser = argparse.ArgumentParser(description='Evaluate Recommender Systems')
parser.add_argument('-r', dest='r', type=str, help="Defaulting to './ratings/count_linear.txt'")
parser.add_argument('-s', dest='s', type=str, help="Defaulting to 'sobazar.tab.prod'")

args = parser.parse_args()

if not args.r:
    args.r = './ratings/count_linear.txt'

if not args.s:
    args.s = './sobazar.tab.prod'
    
createEventTypeFile(args.r, args.s)    

