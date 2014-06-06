#!/usr/bin/env python
import csv
import json
from collections import Counter
import re
import pymongo
import sys
import os
# from nltk.stem.snowball import NorwegianStemmer
# from nltk.stem.snowball import EnglishStemmer
# from nltk import wordpunct_tokenize
# from nltk.corpus import stopwords

def get_mongo_db():
  client = pymongo.MongoClient()
  db = client.mydb
  return db["items"]

# stop = stopwords.words('english') + stopwords.words('norwegian')

def determineProductType(product):

    if any(word in ['dress','kjole','kjolen'] for word in product):
        return 1
    elif any(word in ['jeans','trousers','bukse','bukser', 'joggers'] for word in product):
        return 2
    elif any(word in ['skirt','skjrt', 'shorts'] for word in product):
        return 3
    elif any(word in ['jacket','jakke','jakken','blazer', 'bomber'] for word in product):
        return 4
    elif any(word in ['boot','pump','shoe','boots', 'sandals', 'stiletto', 'sandal'] for word in product):
        return 5
    elif any(word in ['sweater','cardigan','jumper','hoody','genser','genseren'] for word in product):
        return 6
    elif any(word in ['shirt','bluse','skjorte','top'] for word in product):
        return 7
    elif any(word in ['tshirt','jersey','trikot','tskjorte', 'tee'] for word in product):
        return 8
    elif any(word in ['hat','beanie','lue','solbriller','veske','bag','belt','scarf','skjerf', 'handbags'] for word in product):
        return 9
    else:
        return 0

def determineMaterial(product):

    if any(word in ['leather', 'skinn', 'skinnimitasjon'] for word in product):
        return 1
    elif any(word in ['cotton', 'bommul'] for word in product):
        return 2
    elif any(word in ['ribbed'] for word in product):
        return 3
    elif any(word in ['denim'] for word in product):
        return 4
    elif any(word in ['wool', 'ull'] for word in product):
        return 5
    elif any(word in ['knit', 'strikket'] for word in product):
        return 7
    elif any(word in ['polyester','polyester','polyestermachine','polyamid'] for word in product):
        return 8
    elif any(word in ['quilted'] for word in product):
        return 9
    elif any(word in ['fleece'] for word in product):
        return 10
    elif any(word in ['suede'] for word in product):
        return 11
    elif any(word in ['linen'] for word in product):
        return 12
    elif any(word in ['spandex','elastan'] for word in product):
        return 13
    elif any(word in ['chiffon', 'velvet', 'silk'] for word in product):
        return 14
    elif any(word in ['nylon'] for word in product):
        return 16
    elif any(word in ['sequin'] for word in product):
        return 17
    elif any(word in ['fur'] for word in product):
        return 18
    else:
        return 0

def determineStyle(product):

    if any(word in ['classic','klassisk', 'button'] for word in product):
        return 1
    elif any(word in ['cool', 'trendy', 'stylish', 'pocket', 'pockets', 'logo', 'graphic', 'printed', 'urban'] for word in product):
        return 3
    elif any(word in ['vintage'] for word in product):
        return 4
    elif any(word in ['elegant', 'elegance', 'luxurious','exclusive', 'sophisticated'] for word in product):
        return 5
    elif any(word in ['modern', 'moderne', 'simple'] for word in product):
        return 6
    elif any(word in ['relaxed', 'comfy', 'loose', 'stretch', 'joggers'] for word in product):
        return 7
    elif any(word in ['sexy','hot', 'exposed', 'seductive', 'straps', 'delicate'] for word in product):
        return 8
    else:
        return 0

def determinePriceGroup(price):

    if price < 200:
        return 1
    elif price < 400:
        return 2
    elif price < 600:
        return 3
    elif price < 800:
        return 4
    elif price < 1000:
        return 5
    elif price < 1500:
        return 6
    elif price >= 1500:
        return 7
    else:
        return 0

def determineColor(product):
    '''
    Tries to determines the color of a product
    based on its description
    '''

    if any(word in ['black', 'sort'] for word in product):
        return 1
    elif any(word in ['grey'] for word in product):
        return 2
    elif any(word in ['blue','navy'] for word in product):
        return 3
    elif any(word in ['white'] for word in product):
        return 4
    elif any(word in ['gold','gullfarget'] for word in product):
        return 5
    elif any(word in ['metallic'] for word in product):
        return 6
    elif any(word in ['silver'] for word in product):
        return 7
    elif any(word in ['floral'] for word in product):
        return 8
    elif any(word in ['leopard'] for word in product):
        return 9
    elif any(word in ['red'] for word in product):
        return 10
    elif any(word in ['pink'] for word in product):
        return 11
    elif any(word in ['brown'] for word in product):
        return 12
    elif any(word in ['green'] for word in product):
        return 13
    else:
        return 0

def determineBrand(brand):
    '''
    Returns an integer based on the brand(store) name.
    '''

    brands = ['Bianco',
              'InWear',
              'Cubus',
              'Gina Tricot',
              'Lindex',
              'Bik Bok',
              'Acne',
              'Urban Outfitters',
              'Anton Sport',
              'Moods of Norway',
              'Cubus',
              'Express',
              'Americal Eagle']
    for i in range(len(brands)):
        if brand == brands[i]:
            return i+1
    return 0



def readProductData():

    #separator
    s = '}'
    products_json = []

    with open('../data/products.txt', 'r') as file:

        json_data = file.read()
        lines = [e + s for e in json_data.split(s) if e != ""]

        for line in lines:
            products_json.append(json.loads(line))

        print('Read %d products from file' %(len(products_json)))

    return filterProducts(products_json)


def getProductsMongoDb(col):
    return col.find()

def getProductsFile(filename):
    products = {}
    with open(filename, 'r') as f:
      for line in f.readlines():
        j = json.loads(line)
        products[int(j['id'])] = j
    return products

def filterProducts(products_json):
    '''
    Filter out 404 responses from the product list
    '''
    prev = len(products_json)
    products_json = [product for product in products_json if not product.has_key('status')]
    print('Filtered out %d products' %(prev-len(products_json)))
    return products_json


def countBrandNames(products_json):
    '''
    Counts the number of products from each store
    '''
    brandCounter = Counter()
    for product in products_json:
        brandCounter[product['brandName']] += 1
    print (brandCounter)

def priceRangeDistribution(products_json):
    '''
    Finds the price distribution of the products
    '''

    ranges = [200, 400, 600, 800, 1000, 1200, 1500, 25000]
    distribution = [0] * len(ranges)

    for product in products_json:
        for i in range(len(ranges)):
            if float(product['newPrice'] <= ranges[i]):
                distribution[i] += 1
                break

    print (distribution)

def averageDescriptionLength(products_json):
    '''
    Finds the average description length
    (number of characters) for all products
    '''

    totalLength = 0
    for products in products_json:
        totalLength += len(products['description'])
        totalLength += len(products['title'])
        totalLength += len(products['metaDescription'])

    print ('Average product description length: %d' %(totalLength / len(products_json)))

def get_keywords(product):
  title = product.get('title', '').split()
  desc = product.get('description', '').split()
  mdesc = product.get('metaDescription', '').split()
  description = title + desc + mdesc
  keywords = []
  for word in description:
    keywords.append(re.sub(r'\W+', '', word.lower()))
  return keywords

def extractFeatures(products_json, ratings, col):
    '''
    Attemps to extracts the following features
    <id><priceGroup><brand><Color><Style><Material><productType>
    '''
    print('Extracting product features from product database')

    products_json = countMatchingItems(ratings, products_json, col)

    products = []

    for p in products_json:
        # Get a list of keywords for this product, based on title, description
        # and meta-description.
        keywords = get_keywords(p)

        product = []

        #1: Product id
        product.append(int(p['id']))

        #2: Product price group
        product.append(determinePriceGroup(int(p['newPrice'])))

        #3: Product brand
        if 'brandName' in p:
            product.append(determineBrand(p['brandName']))
        else:
            product.append(0)

        #4: Product color
        product.append(determineColor(keywords))

        #5: Product style
        product.append(determineStyle(keywords))

        #6: Product material
        product.append(determineMaterial(keywords))

        #7: Product type
        product.append(determineProductType(keywords))

        # Append the list of features to list of products
        products.append(product)

    return products

def extractTopKeywords(products, num_keywords):

    englishCounter = Counter()
    norwegianCounter = Counter()

    nStemmer = NorwegianStemmer()
    eStemmer = EnglishStemmer()

    for p in products:

        language = 'english'

        if p['description']:
            language = detect_language(p['description'])

        englishKeywords = []
        norwegianKeywords = []

        if language=='english':

            if len(p['title']) > 0:
                englishKeywords = p['title'].split()
            if len(p['description']) > 0:
                englishKeywords.extend(p['description'].split())
            if len(p['metaDescription']) > 0:
                englishKeywords.extend(p['metaDescription'].split())

        else:
            if len(p['title']) > 0:
                norwegianKeywords = p['title'].split()
            if len(p['description']) > 0:
                norwegianKeywords.extend(p['description'].split())
            if len(p['metaDescription']) > 0:
                norwegianKeywords.extend(p['metaDescription'].split())



        for keyword in norwegianKeywords:
            keyword = re.sub(r'\W+', '', keyword.lower())
            #keyword = nStemmer.stem(keyword)
            if keyword not in stop and keyword:
                norwegianCounter[keyword] += 1

        for keyword in englishKeywords:
            keyword = keyword.lower()
            keyword = re.sub(r'\W+', '', keyword.lower())
            #keyword = eStemmer.stem(keyword)
            if keyword not in stop and keyword:
                englishCounter[keyword] += 1

    writeCounterToFile(englishCounter)
    #writeCounterToFile(norwegianCounter)
    #print(englishCounter)
    #print(norwegianCounter)


def createMyMediaLiteAttributeFile(products):
    additions = [0,20,40,60,80,100,120]
    with open('../data/mymedialite_features.txt', 'wb') as file:
        writer =  csv.writer(file, delimiter='\t')
        for product in products:
            for i in range(len(product)-1):
                if product[i] != 0:
                    writer.writerow([product[0], product[i+1]+additions[i]])

def countNonZeroAttributes(attributes):
    counts = [0,0,0,0,0,0]
    for item in attributes:
        if item[1] != 0:
            counts[0] += 1
        if item[2] != 0:
            counts[1] += 1
        if item[3] != 0:
            counts[2] += 1
        if item[4] != 0:
            counts[3] += 1
        if item[5] != 0:
            counts[4] += 1
        if item[6] != 0:
            counts[5] += 1

    counts = [x/float(len(attributes)) for x in counts]
    print('Price, Brand, Color, Style, Matrial, ProductType')
    print(counts)


def countMatchingItems(ratings, products, col):
    print('Counting matching, dropping the "dead" ones')
    count = 0
    items = {}
    prod_cleaned = []

    for rating in ratings:
        if not items.get(rating[1], None):
            items[rating[1]] = 1

    if not col:
      # File-mode
      for key, value in products.iteritems():
        if items.get(key, None):
          count += 1
          prod_cleaned.append(value)
    else:
      # Using mongo-db
      for product in products:
          if int(product['id']) in items:
              count += 1
              prod_cleaned.append(product)
          else:
              # Remove form Mongo
              col.remove({'id': product['id']})

    print('Number of matching items: %d' %count)
    return prod_cleaned

def readSobazarRatings(path):
    ratings = []
    f = open(path, 'r+')
    reader = f.readlines()
    f.close()
    for tmp in reader:
        rating = tmp.split('\t')
        # print (rating)
        # sys.exit()
        if len(rating) >= 3:
          ratings.append([int(rating[0]), int(rating[1]), float(rating[2])])
        else:
          print "The input ratings are on a wrong format (less than two columns). Exiting."
          sys.exit(1)
    # for line in lines:
    #     tmp = line.split(',')
    #     predictions.append([int(tmp[0]), int(tmp[1]), float(tmp[2])])

    # with open(path, 'r') as file:
    #     dialect = csv.Sniffer().sniff(file.read(2048))
    #     reader =  csv.reader(file, delimiter='\t')
    #     for rating in reader:
    #         print (rating)
    #         if len(rating) >= 3:
    #           ratings.append([int(rating[0]), int(rating[1]), float(rating[2])])
    #         else:
    #           print "The input ratings are on a wrong format (less than two columns). Exiting."
    #           sys.exit(1)
    return ratings


def detect_language(text):
    ratios = calculate_language_ratios(text)
    return max(ratios, key=ratios.get)

def writeCounterToFile(c):
    with open('../data/topwords.txt', 'wb') as file:
        for k,v in c.most_common():
            file.write( "{} {}\n".format(k,v) )

def calculate_language_ratios(text):

    languages_ratios = {}
    tokens = wordpunct_tokenize(text)
    words = [word.lower() for word in tokens]

    # Compute per language included in nltk number of unique stopwords appearing in analyzed text
    for language in stopwords.fileids():
        stopwords_set = set(stopwords.words(language))
        words_set = set(words)
        common_elements = words_set.intersection(stopwords_set)

        languages_ratios[language] = len(common_elements) # language "score"

    return languages_ratios


def writeProductsToFile(filename, products):
    """
      Write a set of features for every product. The products array looks like:

      11111000      0       1       1       1         1

      Which maps to the following properties:

      product_id    price  brand    color   material  product_type
    """
    with open(filename, 'wb') as f:
        writer =  csv.writer(f, delimiter='\t')
        writer.writerows(products)

def main():
    SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
    ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)
    GENERATED_LOCATION = 'generated'

    RATING_FILE = ROOT_FOLDER + '/' + GENERATED_LOCATION + '/' + 'ratings/blend.txt'
    OUT_FILE = ROOT_FOLDER + '/' + GENERATED_LOCATION + '/' + 'itemFeatures.txt'
    products_json = None

    # Check if we want to generate from file or mongodb
    MONGO_DB, col = True, 'items'
    PRODUCT_FILE = ''
    if len(sys.argv) > 1:
      PRODUCT_FILE = sys.argv[1]
      MONGO_DB, col = False, None

    # Read the JSON-data of product descriptions from file or DB.
    if MONGO_DB:
      col = get_mongo_db()
      products_json = getProductsMongoDb(col)
    else:
      products_json = getProductsFile(PRODUCT_FILE)

    # Get the ratings from a rating file.
    ratings = readSobazarRatings(RATING_FILE)

    # Use the ratings and product-descriptions in order to extract features.
    products = extractFeatures(products_json, ratings, col)

    # Write feature-file
    writeProductsToFile(OUT_FILE, products)

if __name__ == "__main__":
    main()
