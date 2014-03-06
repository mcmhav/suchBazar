import re
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
    
        
products_json = readProductData()



#averageDescriptionLength(products_json)
#countBrandNames(products_json)
#priceRangeDistribution(products_json)
