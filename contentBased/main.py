import re
import csv
import json
from collections import Counter
import array

def readProductData():
    
    #separator
    s = '}'
    products_json = []
    
    with open('Data/products.txt', 'r') as file:
        
        json_data = file.read()
        lines = [e + s for e in json_data.split(s) if e != ""]
        
        for line in lines:
            products_json.append(json.loads(line))          
        
        print('Read %d products from file' %(len(products_json)))
    
    return filterProducts(products_json)


def filterProducts(products_json):
    '''
    Filter out 404 responses from the product list
    '''
    prev = len(products_json)
    products_json = [product for product in products_json if not product.has_key('status')]
    print('Filtered out %d products' %(prev-len(products_json)))
    return products_json
    

def countBrandNames(products_json):
    brandCounter = Counter()
    for product in products_json:
        brandCounter[product['brandName']] += 1
    print (brandCounter)
        
def priceRangeDistribution(products_json):
    
    ranges = [200, 400, 600, 800, 1000, 1200, 1500, 25000]
    distribution = [0] * len(ranges)
    
    for product in products_json:
        for i in range(len(ranges)):
            if float(product['newPrice'] <= ranges[i]):
                distribution[i] += 1
                break
            
    print (distribution)               
        
def averageDescriptionLength(products_json):
    
    totalLength = 0
    for products in products_json:
        totalLength += len(products['description'])
    
    print ('Average product description length: %d' %(totalLength / len(products_json)))
    
'''
 Which features to use?
 id
 brandName
 title
 description
 newPrice
 targetGender
 targetAgeGroup
 metaDescription
 '''   
def extractFeatures(products_json):
    
    products = []
    
    for p in products_json:
        product = []
        product.append(p['id'])
        product.append(p['brandName'])
        product.append(p['title'])
        product.append(p['description'])
        product.append(p['newPrice'])
        product.append(p['targetGender'])
        product.append(p['targetAgeGroup'])
        product.append(p['metaDescription'])
        products.append(product)
        
    writeProductsToFile(products)
        
def writeProductsToFile(products):

    with open('./Data/product_features.txt', 'wb') as file:
        writer =  csv.writer(file, delimiter='\t')
        writer.writerows([unicode(s).encode('utf-8') for s in products])
        
products_json = readProductData()
extractFeatures(products_json)



#averageDescriptionLength(products_json)
#countBrandNames(products_json)
#priceRangeDistribution(products_json)
