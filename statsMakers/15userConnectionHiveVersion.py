import sys
import argparse
import helpers
import json
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Construct Training, Validation and Prediction files from mongoDB.')
parser.add_argument('-col', type=str, default="cleanedItems")
args = parser.parse_args()

col = helpers.getCollection(args.col)

print ("Collection used: ", args.col)
print ("")

total = 0

def main():
    handleStraight()


def handleStraight():
    users = col.distinct('user_id')
    total = len(users)

    theJson = []

    nodes = placeUserNodes(users,total)

    links = makeLinks(users,total,nodes)

    writeToJson(nodes,'nodes')
    writeToJson(links,'links')

def makeLinks(users,total,nodes):
    links = []
    handledUsers = []
    count = 0
    for user in users:
        userItems = col.find({'user_id':user}).distinct('product_id')

        for userItem in userItems:
            usersWithItem = col.find({'product_id':userItem}).distinct('user_id')
            usersWithItemstr = []
            for u in usersWithItem:
                if str(u) != str(user) and not u in handledUsers:
                    links.append({'source':count,'target':findPosOfUser(u,users)})
        count += 1
        handledUsers.append(str(user))
        helpers.printProgress(count,total)

    return links

def findPosOfUser(user,users):
    count = 0
    for u in users:
        if user == u:
            return count
        count += 1
    return -1

def placeUserNodes(users,total):
    nodeRange = total/3
    x = 0
    nodes = []
    count = 0

    for user in users:
        y = (count-(nodeRange*x))/nodeRange
        hiveLocation = {'x': x, 'y': y}
        nodes.append(hiveLocation)
        count += 1
        if count > nodeRange*(x+1):
            x+=1
    return nodes

def writeToJson(jsonObj,name):
    e = open(name + '.json','w')
    e.write(json.dumps(jsonObj, indent=4, separators=(',', ': ')))
    e.close()

def handleWithGroups():
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

def handleWithMR():
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


if __name__ == "__main__":
    main()


# [
#     {
#         "type"    : "view",
#         "name"    : "1234", #user id
#         "depends" : [
#             "2345",
#         ]
#     }, {
#         "type"    : "view",
#         "name"    : "2345",
#         "depends" : [
#         ]
#     },{
#         "type"    : "view",
#         "name"    : "3456",
#         "depends" : [
#         ]
#     }
# ]
