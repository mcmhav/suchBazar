import json
import pymongo
import csv
import argparse
import os
import sys
from bson import Binary, Code
import helpers
import matplotlib.pyplot as plt
import numpy as np

def main(sessDB='sessionsNew'):
    groups = groupEventsWithStores(sessDB)

    for group in groups:
        print (group['event_id'])

    sys.exit()

# def makeEvent

def groupEventsWithStores(sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1;
                        result.storeCount[cur.storefront_name] += 1;
                    }
                   """)
    k = 'event_id'
    groups = col.group(
                           key={k:1},
                           condition={'$and':[
                                {k:{'$ne':'NULL'}},
                                {k:{'$ne':'N/A'}},
                                {k:{'$ne':''}}
                            ]},
                           reduce=reducer,
                           initial={'count':0,'storeCount':{
        "NULL":0,
        "Cubus":0,
        "":0,
        "Express":0,
        "Bik Bok":0,
        "Gina Tricot":0,
        "Bianco Footwear":0,
        "Reiss":0,
        "Revolve Clothing":0,
        "Superdry":0,
        "Urban Outfitters":0,
        "The Limited":0,
        "Moods of Norway":0,
        "Anton Sport":0,
        "BIK BOK":0,
        "Inwear":0,
        "Mood of Cambodia":0,
        "Mood of Cambodia_disable":0,
        "Luisa Via Roma":0,
        "French Connection":0,
        "H&M":0,
        "SO CITY WEEKEND":0,
        "American Eagle":0,
        "SO FESTIVAL":0,
        "Editor´s Picks":0,
        "NEW THIS WEEK":0,
        "UO Coming Soon":0,
        "DARK LUXURY":0,
        "HALLELUJAH":0,
        "Key pieces":0,
        "Premium Quality":0,
        "Superdry Coming Soon":0,
        "Mary-Kate & Ashley Olsen Third Collection":0,
        "Ready for a party?":0,
        "Party Collection":0,
        "Moods OL KOLLEKSJONEN":0,
        "Urban Outfitters 2":0,
        "Moods New arrivals":0,
        "Kari Traa Anton sport":0,
        "H&M Sunny Getaway":0,
        "H&M New arrivals":0,
        "H&M Key pieces":0,
        "H&M GO ATHLETIC":0,
        "H&M Feminine Finesse":0,
        "Gina Tricot Weekend Glow":0,
        "Gina Tricot Spring preview":0,
        "Gina Tricot Preppy Perfect":0,
        "Gina Casual Ease":0,
        "Editor´ s Picks":0,
        "CUBUS Undertøy":0,
        "CUBUS New arrivals":0,
        "Bianco Geometric":0,
        "BIK BOK Only 99:0,-":0,
        "BIK BOK New Arrivals":0,
        "BIANCO New arrivals":0,
        "Anton sport Nike":0,
        "Anton Sport Sesongen Nyheter":0,
        "Acne Studios LIVE":0,
        "AE New Arrivals":0,
        "Superdry Timothy Everest":0,
        "BIK BOK Sale":0,
        "BIK BOK Valentines":0,
        "CUBUS":0,
        "COMING SOON CUBUS":0,
        "Gina tricot Active Sports":0,
        "Lindex Best sellers":0,
        "Lindex Sale":0,
        "Lindex Tomorrow":0,
        "LindexStreet Chic":0,
        "Maritime Touch":0,
        "New Arrivals Acne":0,
        "Reiss New Arrivals":0,
        "Superdry New ins":0,
        "Reiss Sale":0,
        "Bianco DARK LUXURY":0,
        "Gina Tricot Grand prix":0,
        "Anton Sport Bergans":0,
        "Bianco":0,
        "Lindex":0,
        "Acne":0,
        "Storefront_Test":0,
        "Editors´ Picks":0,
        "Acne Studios":0,
        "GO ATHLETIC":0,
        "OL KOLLEKSJONEN":0,
        "BIK BOK Westhill Redbird":0,
        "Best sellers Lindex":0,
        "Active Sports Gina tricot":0,
        "Casual Ease":0,
        "Gina Tricot 3 for 99 kr":0,
        "Bik Bok Mary-Kate & Ashley Olsen Third Collection":0,
        "Bianco SALE":0,
        "Sale BIKBOK":0,
        "Sale Moods":0,
        "H&M Pure Elegance":0,
        "H&M Premium Quality":0,
        "CUBUS SALE":0,
        "Inwear spring arrivals":0,
        "H&M Western Chic":0,
        "SALE":0,
        "H&M Spring Styles":0,
        "New Arrivals":0,
        "New Arrivals AE":0,
        "BIK BOK 100kr discount":0,
        "Editors picks Valentines day":0,
        "Gina Tricot New arrivals":0,
        "CUBUS PRETTY IN PINK":0,
        "Bianco Accessories":0,
        "Cubus Acessories":0,
        "Gina Feminine Fit":0,
        "100kr discount":0,
        "3 for 99 kr":0,
        "Accessories":0,
        "Best sellers":0,
        "Conscious Exclusive":0,
        "Fitness":0,
        "New arrivals":0,
        "Only 99:0,-":0,
        "Preppy Perfect":0,
        "Pretty in Pink":0,
        "Sale":0,
        "SALE Bianco":0,
        "Nike Anton sport":0,
        "Sale Reiss":0,
        "Inwear Ready for a party?":0,
        "inwear berry shades":0,
        "Urban The Dress edit":0,
        "Urban Outfitters New Arrivals":0,
        "SOFESTIVAL":0,
        "SOCITYWEEKEND":0,
        "Reiss New arrivals":0,
        "Reiss New Collection":0,
        "Morsdag":0,
        "Moods Sport":0,
        "HM Go athletic":0,
        "Cubus Fitness":0,
        "New arrivals Gina":0,
        "New Arrivals Lindex":0,
        "Weekend Glow":0,
        "Lindex New Arrivals":0,
        "Gina tricot Tough Romance":0,
        "H&M Contemporary cool":0,
        "Feminine Finesse":0,
        "Angelica Blick":0,

                           }}
                       )


    return groups

def groupStoreEvents(sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1;
                        tmp = result.eventCount;
                        currentEventId = cur.event_id;
                        test = (tmp.hasOwnProperty(currentEventId));
                        if (!test){
                            result.eventCount[cur.event_id] = 0;
                        }
                        result.eventCount[cur.event_id] += 1;
                    }
                   """)
    k = 'storefront_name'
    groups = col.group(
                           key={k:1},
                           condition={'$and':[
                                {k:{'$ne':'NULL'}},
                                {k:{'$ne':'N/A'}},
                                {k:{'$ne':''}}
                            ]},
                           reduce=reducer,
                           initial={'count':0,'eventCount':{}}
                       )
    return groups

def makePlot(groups,k):
    '''
    '''
    ks = [str(x[k]) for x in groups]
    counts = [int(x['count']) for x in groups]
    if (k == 'storefront_name'):
        i = 0
        tmpCounts = counts[:]
        for count in counts:
            if (count < 200):
                del tmpCounts[i]
                del ks[i]
                i -= 1
            i += 1
        counts = tmpCounts[:]

    index = np.arange(len(counts))
    width = 0.8

    fig, ax = plt.subplots()
    fig.set_size_inches(14.0,8.0)
    plt.bar(index, counts, width)
    plt.title("Events id distribution")

    plt.xticks(index+width/2., ks)
    plt.ylabel('Event count')
    plt.xlabel('Event id')
    # ax.set_xticks(range(0,len(counts)+2))

    fig.autofmt_xdate()
    # ax.set_xticklabels(ks)

    plt.axis([0, len(ks), 0, max(counts) + (max(counts)/100)])
    plt.grid(True)
    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/" + k + "distribution.png"
    plt.savefig(location)
    plt.show()
    print ('Price distribution written to: %s' % location)
    N = 5
    menMeans   = (20, 35, 30, 35, 27)
    womenMeans = (25, 32, 34, 20, 25)
    menStd     = (2, 3, 4, 1, 2)
    womenStd   = (3, 5, 2, 3, 3)
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, menMeans,   width, color='r', yerr=womenStd)
    p2 = plt.bar(ind, womenMeans, width, color='y',
                 bottom=menMeans, yerr=menStd)

    plt.ylabel('Scores')
    plt.title('Scores by group and gender')
    plt.xticks(ind+width/2., ('G1', 'G2', 'G3', 'G4', 'G5') )
    plt.yticks(np.arange(0,81,10))
    plt.legend( (p1[0], p2[0]), ('Men', 'Women') )

    plt.show()


def getLabelFromItemDB(bids):
    labels = []
    col = helpers.getCollection('brandstaging')

    for bid in bids:
        for dbId in col.find():
            if (bid) == str(float(dbId['id'])):
                labels.append(dbId['displayName'])
    return labels

useVals = {
    "storefront_name",
}

if __name__ == "__main__":
    main()
