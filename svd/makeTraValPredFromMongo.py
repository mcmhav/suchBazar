import sys
import argparse
import helpers
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Construct Training, Validation and Prediction files from mongoDB.')
parser.add_argument('-sc', type=str, default="cleanedItems")
parser.add_argument('-c', type=str, default="userItemRating.csv")
args = parser.parse_args()

sessCol = helpers.getCollection(args.sc)

print ("Collection used: ", args.sc)
print ("Output file:     ", args.c)
print ("")

total = 0

def main():
    handleItemAndUserMapReduce()
    # handleUsersSlow() #superslow, does the same as the one above

def handleItemAndUserMapReduce():
    mapper = Code(  """
            function () {
                key = this.user_id + "\t" + this.product_id;
                if (this.event_id == 'product_purchase_intended'){
                    emit(key, 10);
                } else if (this.event_id == 'product_wanted'){
                    emit(key, 5);
                } else if (this.event_id == 'product_detail_clicked'){
                    emit(key, 1);
                }

            }
        """)

    reducer = Code( """
                    function (key, values) {
                        var total = 0;
                        for (var i = 0; i < values.length; i++) {
                            total += values[i];
                        }
                        return total;
                    }
                    """)
    result = sessCol.map_reduce(mapper, reducer, "myresults")
    f = open(args.c, 'a')
    for r in result.find():
        f.write("%s\t%s\n" % (r['_id'], int(r['value'])))
    f.close()
    print (result.find().count())

def handleUsersSlow():
    users = sessCol.distinct('user_id')

    gReducer = Code("""
        function (cur,result) {
            result.count += 1
        }
       """)
    total = len(users)
    count = 0
    handleItemAndUserMapReduce(mapper,reducer)
    f = open(args.c, 'a')
    for user in users:
        items = sessCol.find({'user_id':user}).distinct('product_id')
        for item in items:
            eventGoups = handleItemAndUserSlow(gReducer, user, item)
            rating = findRating(eventGoups)
            writeToFile(user,item,rating,f)

        count += 1
        helpers.printProgress(count,total)
    f.close()

def handleItemAndUserSlow(reducer,user,item):
    eventGoups = sessCol.group(
       key={'event_id':1},
       condition={'user_id':user,'product_id':item,'$or':[{'event_id':'product_purchase_intended'}, {'event_id':'product_wanted'},{'event_id':'product_detail_clicked'}]},
       reduce=reducer,
       initial={'count':0}
   )
    return eventGoups

def findRating(eventGoups):
    rating = 0
    for events in eventGoups:
        rating += utils.translate_events([events['event_id']]) * events['count']
    return rating

def writeToFile(user,item,rating,f):
    if rating > 0:
        f.write("%s\t%s\t%s\n" % (user, item, rating))

if __name__ == "__main__":
    main()
