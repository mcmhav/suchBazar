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
    2: "stores_map_clicked",
    3: "product_detail_clicked",
    4: "product_purchase_intended",
    5: "store_clicked",
}

def main():
    stores = sessCol.distinct('retailer_brand')

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
                           condition={'retailer_brand':store},
                           reduce=reducer,
                           initial={'count':0}
                       )
    for g in groups:
        print (g)
    storeEvents = {}
    storeEvents['name'] = store
    storeEvents['children'] = []
    for e in groups:
        storeEvents['children'].append(convertEventToFlare(e))

    return storeEvents

def convertEventToFlare(e):
    return {'name':e['event_id'],'size':e['count']}

def writeToCSV(sJson):
    cs = helpers.getCSVWriter('stats/retailerStoreEvents')
    cs.writerow(['',uSE[1],uSE[2],uSE[3],uSE[4],uSE[5]])
    for c in sJson['children']:
        pw = 0
        sm = 0
        pd = 0
        pp = 0
        sc = 0
        for e in c['children']:
            if e['name'] == 'product_wanted':
                pw = e['size']
            elif e['name'] == 'stores_map_clicked':
                sm = e['size']
            elif e['name'] == 'product_detail_clicked':
                pd = e['size']
            elif e['name'] == 'product_purchase_intended':
                pp = e['size']
            elif e['name'] == 'store_clicked':
                sc = e['size']
        cs.writerow([c['name'],pw,sm,pd,pp,sc])
    helpers.closeF()

if __name__ == "__main__":
    main()
