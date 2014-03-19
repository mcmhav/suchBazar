import sys
import argparse
import helpers
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Clean items.')
parser.add_argument('-sc', type=str, default="sessions")
parser.add_argument('-oc', type=str, default="offerstaging")
parser.add_argument('-cic', type=str, default="cleanedItems")
parser.add_argument('-c', type=str, default="outMF.csv")
args = parser.parse_args()

sessCol = helpers.getCollection(args.sc)
itemCol = helpers.getCollection(args.oc)
cleanCol = helpers.getCollection(args.cic)
cleanCol.remove()

print ("Collection used: ", args.sc)
print ("Output file:     ", args.c)
print ("")

productNameFilter = ['Free', 'Giftcard', 'Offer', 'Test', 'NULL']
#Only accept activity originating from the following countries
countryFilter = ['Norway', 'NULL', 'N/A']
#Only accept the following event_ids
eventFilter = ['product_detail_clicked', 'product_wanted', 'product_purchase_intended', 'featured_product_clicked', 'product_purchased']

total = 0

def main():
    events = sessCol.find()
    items = itemCol.distinct('id')
    # for i in items:
    #     print (i)
    total = events.count()
    count = 0
    for event in events:
        if str(event['product_id']) in items and validateEvent(event):
            cleanCol.insert(event)
        count += 1
        helpers.printProgress(count,total)
    #Do    handleItemAndUserMapReduce()

def validateEvent(event):
    prodId = event['product_id']
    eventId = event['event_id']
    prodName = event['product_name']
    country = event['country_name']

    if not eventId in eventFilter:
        return False

    if prodId == 'NULL' or prodId == 'null' or prodId == "N/A":
        return False

    if any(s in prodName.split() for s in productNameFilter):
        return False

    if not country in countryFilter:
        return False

    return True

if __name__ == "__main__":
    main()
