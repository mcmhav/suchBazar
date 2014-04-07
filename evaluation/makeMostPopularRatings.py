import sys
import argparse
import helpers
from bson import Binary, Code
from operator import itemgetter

parser = argparse.ArgumentParser(description='Construct Training, Validation and Prediction files from mongoDB.')
parser.add_argument('-sc', type=str, default="sessions")
parser.add_argument('-c', type=str, default="outMF.csv")
args = parser.parse_args()

col = helpers.getCollection(args.sc)

print ("Collection used: ", args.sc)
print ("Output file:     ", args.c)
print ("")

total = 0

def main():
    makeSimpleItemsRatings()

def makeSimpleItemsRatings():
    """
    Make a simple item recommendation for testing purposes
    Using most popular approach
    Unnecessary user to rating mapping, but meant to be as close to the personalized recommendations

    change to:
        user, item, rating
    """


    users = col.distinct('user_id')
    ratings = {}
    userRatings = getRatingsForUser("")
    e = open('mostPopular' + '.ratings','w')

    # e.write("user, item, rating" + "\n")

    for user in users:
        for itemRating in userRatings:
            item = str(int(itemRating['_id']))
            rating = str(int(itemRating['value']))
            e.write(str(int(user)) + "," + item + "," + rating + "\n")

    e.close()
    return ratings

def getRatingsForUser(user):
    tmp = sorted(mostPopularMR().find(), key=itemgetter('value'),reverse=True)
    return tmp


def mostPopularMR():
    mapper = Code(  """
        function () {
            key = this.product_id;
            if (this.event_id == 'product_purchase_intended'){
                emit(key, 20);
            } else if (this.event_id == 'product_wanted'){
                emit(key, 15);
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
    result = col.map_reduce(mapper, reducer, "myresults")
    return result


if __name__ == "__main__":
    main()
