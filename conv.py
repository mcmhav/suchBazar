import json
import pymongo
import argparse

parser = argparse.ArgumentParser(description='Convert tab and insert to mongoDB.')
parser.add_argument('-f', type=str, default="sobev.tab")
parser.add_argument('-c', type=str, default="prod")
args = parser.parse_args()

client = pymongo.MongoClient()
db = client.mydb
col = db[args.c]
col.remove()

print ("File used: ", args.f)
print ("Collection used: ", args.c)

# f = open('test.tab')
f = open(args.f)
head = f.readline().strip().split('\t')

headJson = {}
headJson["head"] = head
col.insert(headJson)

dataJson = []

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

for line in f:
    sl = line.split('\t')
    # print (sl)
    c = 0
    tmpJson = {}
    for val in sl:
        if is_json(val):
        	tmpJson[head[c]] = json.loads(val.strip())
        else:
        	tmpJson[head[c]] = val.strip()
        c = c + 1
    if tmpJson["event_json"]["eventData"]:
    	tmpJson["event_json"]["eventData"] = json.loads(tmpJson["event_json"]["eventData"])

    # dataJson.append(tmpJson)

    if tmpJson['server_environment'] == 'prod':
        col.insert(tmpJson)

f.close()

# e = open(args.f + '.json','w')
# e.write(json.dumps(dataJson, indent=4, separators=(',', ': ')))
# e.close()

# print json.dumps(dataJson, sort_keys=True, indent=4, separators=(',', ': '))
