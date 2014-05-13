from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import helpers
import argparse
from bson import Binary, Code
import matplotlib.pyplot as plt
import os

parser = argparse.ArgumentParser(description='Write price distribution to file.')
parser.add_argument('-sc', type=str, default="sessions")
parser.add_argument('-l', type=str, default='data/stats/priceDistribution')
args = parser.parse_args()

col = helpers.getCollection(args.sc)

# print ("Collection used: ", args.sc)
# print ("")

def main():

    priceBuckets = [0] * 3001
    priceCounts = findPriceForItems()

    for price in priceCounts:
        if int(price['price']) > 3000:
            priceBuckets[3000] += int(price['count'])
        else:
            priceBuckets[int(price['price'])] = int(price['count'])

    w = helpers.getCSVWriter(args.l)
    c = 0
    yaxis = []
    for price in priceBuckets:
        w.writerow([c,price])
        yaxis.append(c)
        c += 1

    helpers.closeF()
    plotIt(priceBuckets,yaxis)

def plotIt(priceBuckets,yaxis):
    fig, ax = plt.subplots()
    fig.set_size_inches(14.0,8.0)
    plt.plot(yaxis, priceBuckets, 'r')
    plt.title('Price Distribution')
    plt.ylabel('Amount Of Items')
    plt.xlabel('Price')
    plt.axis([0, 3010, 0, 1600])
    plt.grid(True)
    # plt.show()
    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/priceDistribution.png"
    plt.savefig(location)
    print ('Price distribution written to: %s' % location)

def findPriceForItems():
    gReducer = Code("""
        function (cur,result) {
            result.count += 1
        }
    """)
    eventGoups = col.group(
        key={'price':1},
        condition={'$and':[
            {'price':{'$ne':'NULL'}},
            {'price':{'$ne':'N/A'}}
        ]},
        reduce=gReducer,
        initial={'count':0}
    )

    return eventGoups

if __name__ == "__main__":
    main()
