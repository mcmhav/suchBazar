import csv
import json
from collections import Counter
import re
from nltk.stem.snowball import NorwegianStemmer
from nltk.stem.snowball import EnglishStemmer
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords

stop = stopwords.words('english') + stopwords.words('norwegian')

def determineProductType(product):
        
    if any(word in ['dress','kjole','kjolen'] for word in product):
        return 1
    elif any(word in ['jeans','trousers','bukse','bukser'] for word in product):
        return 2
    elif any(word in ['skirt','skjrt'] for word in product):
        return 3
    elif any(word in ['jacket','jakke','jakken','blazer'] for word in product):
        return 4
    elif any(word in ['boot','pump','shoe','boots'] for word in product):
        return 5
    elif any(word in ['sweater','cardigan','jumper','hoody','genser','genseren'] for word in product):
        return 6
    elif any(word in ['shirt','bluse','skjorte','top'] for word in product):
        return 7
    elif any(word in ['tshirt','jersey','trikot','tskjorte'] for word in product):
        return 8
    elif any(word in ['scarf','skjerf'] for word in product):
        return 9
    elif any(word in ['shorts'] for word in product):
        return 10
    elif any(word in ['hat','beanie','lue','solbriller','veske','bag','belt'] for word in product):
        return 11
    else:
        return 0

def determineMaterial(product):
   
    if any(word in ["leather", "skinn", 'skinnimitasjon'] for word in product):
        return 1
    elif any(word in ['cotton', 'bommul'] for word in product):
        return 2
    elif any(word in ['ribbed'] for word in product):
        return 3
    elif any(word in ['denim'] for word in product):
        return 4
    elif any(word in ['wool', 'ull'] for word in product):
        return 5
    elif any(word in ['silk'] for word in product):
        return 6
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
    elif any(word in ['chiffon'] for word in product):
        return 14
    elif any(word in ['velvet'] for word in product):
        return 15
    elif any(word in ['nylon'] for word in product):
        return 16
    elif any(word in ['sequin'] for word in product):
        return 17
    elif any(word in ['fur'] for word in product):
        return 18
    else:
        return 0
    


def determineStyle(product):
    
    if any(word in ['classic','klassisk'] for word in product):
        return 1
    elif any(word in ['cool'] for word in product):
        return 2
    elif any(word in ['stylish'] for word in product):
        return 3
    elif any(word in ['fitted'] for word in product):
        return 4
    elif any(word in ['vintage'] for word in product):
        return 5
    elif any(word in ['elegant'] for word in product):
        return 6
    elif any(word in ['simple'] for word in product):
        return 7
    elif any(word in ['modern', 'moderne'] for word in product):
        return 8
    elif any(word in ['relaxed'] for word in product):
        return 9
    elif any(word in ['luxurious','exclusive'] for word in product):
        return 10
    elif any(word in ['trendy'] for word in product):
        return 11
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
    else:
        return 0
    
def determineBrand(brand):
       
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
    


def extractFeatures(products_json):
    '''
    Attemps to extracts the following features
        id
        brand
        pricegroup
        color
        style
        material
        producttype
    '''
    
    products = []
    
    for p in products_json:
    
        product = []
        keywords = []
        
        description = p['title'].split() + p['description'].split() + p['metaDescription'].split()
        for word in description:
            keywords.append(re.sub(r'\W+', '', word.lower()))
        
        product.append(int(p['id']))
        product.append(determinePriceGroup(int(p['newPrice'])))
        product.append(determineBrand(p['brandName']))
        product.append(determineColor(keywords))
        product.append(determineStyle(keywords))
        product.append(determineMaterial(keywords))
        product.append(determineProductType(keywords))
        
        print(product)

        products.append(product)
        
    writeProductsToFile(products)
        
def extractTopKeywords(products, num_keywords):
    
    englishCounter = Counter()
    norwegianCounter = Counter()
    
    nStemmer = NorwegianStemmer()
    eStemmer = EnglishStemmer()
        
    for p in products_json:
        
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
            
    #writeCounterToFile(englishCounter)
    #writeCounterToFile(norwegianCounter)
    #print(englishCounter)
    #print(norwegianCounter)
    
            

def detect_language(text):
    ratios = calculate_language_ratios(text)
    return max(ratios, key=ratios.get)

def writeCounterToFile(c):
    with open('./Data/topwords.txt', 'wb') as file:
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
            
def createProductFeatureFile(products):
    '''
    <itemid><feature>...<feature>
    '''            
    
    
    
        
def writeProductsToFile(products):

    with open('./Data/product_features.txt', 'wb') as file:
        #print(products)
        writer =  csv.writer(file, delimiter='\t')
        writer.writerows(products)
        
products_json = readProductData()
#extractTopKeywords(products_json, 200)
#print(len(products_json))
extractFeatures(products_json)

#keywords = ['jacket', 'penis', 'anal']
#stopwords = ['jacket', 'tits', 'gram']

#if any(word in ['jacket', 'tits', 'gram'] for word in keywords):
#    print('BLACK DICKS IN YOUR ASS')


#averageDescriptionLength(products_json)
#countBrandNames(products_json)
#priceRangeDistribution(products_json)
