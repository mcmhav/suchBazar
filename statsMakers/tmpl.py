import sys
import argparse
import helpers
from bson import Binary, Code

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
    #Do something awesome

    total = len()
    count = 0

    helpers.printProgress(count,total)


def group():
    gReducer = Code("""
        function (cur,result) {
            result.count += 1
        }
   """)
    eventGoups = col.group(
       key={'user_id':1},
       condition={'user_id':user,'product_id':item,'$or':[{'event_id':'product_purchase_intended'}, {'event_id':'product_wanted'},{'event_id':'product_detail_clicked'}]},
       reduce=gReducer,
       initial={'count':0}
   )

def mr():
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
    result = col.map_reduce(mapper, reducer, "myresults")
    return result


if __name__ == "__main__":
    main()
