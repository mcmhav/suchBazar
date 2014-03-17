import json
import csv
import argparse
import os
import sys
from bson import Binary, Code
import helpers

parser = argparse.ArgumentParser(description='Divides each store into 5 children events. Count children and visualize this distribution.')
parser.add_argument('-v',dest='v', action='store_true')
parser.add_argument('-sc',type=str, default="sessions")
parser.add_argument('-t',dest='t', action='store_true')
parser.set_defaults(v=True)
parser.set_defaults(t=False)
args = parser.parse_args()

print ("Verbose:                     %d" % args.v)
print ("Sessions collection used:    %s" % args.sc)
print ("Test run:                    %s" % args.t)
print ("")

sessCol = helpers.getCollection(args.sc)

uSE = {
    1: "product_wanted",
    2: "storefront_clicked",
    3: "product_detail_clicked",
    4: "featured_storefront_clicked",
    5: "product_purchase_intended",
}

def main():
    stores = sessCol.distinct('storefront_name')

    total = len(stores)
    count = 0.0
    sJson = {}
    sJson['name'] = 'flare'
    sJson['children'] = []
    for store in stores:
        if store == 'NULL' or store == '':
            continue
        else:
            sJson['children'].append(someAwesomeName(store))
            count += 1
            helpers.printProgress(count,total)

    writeToFlare(sJson)
    writeToCSV(sJson)

def someAwesomeName(store):
    # db.sessions.group({key:{'event_id':1},cond:{'storefront_name':'Reiss'},reduce:function(cur,result){result.count += 1}, initial: {count:0}})
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = sessCol.group(
                           key={'event_id':1},
                           condition={'storefront_name':store},
                           reduce=reducer,
                           initial={'count':0}
                       )

    storeEvents = {}
    storeEvents['name'] = store
    storeEvents['children'] = []
    for e in groups:
        storeEvents['children'].append(convertEventToFlare(e))

    return storeEvents

def convertEventToFlare(e):
    return {'name':e['event_id'],'size':e['count']}

def writeToFlare(sJson):
    e = open('flare.json','w')
    e.write(json.dumps(sJson, indent=4, separators=(',', ': ')))
    e.close()

def writeToCSV(sJson):
    cs = helpers.getCSVWriter('stats/storeEvents')
    cs.writerow(['',uSE[1],uSE[2],uSE[3],uSE[4],uSE[5]])
    for c in sJson['children']:
        pw = 0
        sc = 0
        pd = 0
        fs = 0
        pp = 0
        for e in c['children']:
            if e['name'] == 'product_wanted':
                pw = e['size']
            elif e['name'] == 'storefront_clicked':
                sc = e['size']
            elif e['name'] == 'product_detail_clicked':
                pd = e['size']
            elif e['name'] == 'featured_storefront_clicked':
                fs = e['size']
            elif e['name'] == 'product_purchase_intended':
                pp = e['size']
        cs.writerow([c['name'],pw,sc,pd,fs,pp])
    helpers.closeF()

if __name__ == "__main__":
    main()
