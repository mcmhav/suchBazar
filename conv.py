import json
import argparse
import sys
from statsMakers import helpers

parser = argparse.ArgumentParser(description='Convert tab and insert to mongoDB.')
parser.add_argument('-f', type=str, default="dbFiles/sobev.tab")
parser.add_argument('-c', type=str, default="prod")
args = parser.parse_args()

col = helpers.getCollection(args.c,True)

print ("File used: ", args.f)
print ("Collection used: ", args.c)
print ("")

def main():
    f = open(args.f)
    head = f.readline().strip().split('\t')

    headJson = {}
    headJson["head"] = head
    col.insert(headJson)

    lines = f.readlines()
    f.close()

    total = len(lines)
    count = 0

    for line in lines:
        sl = line.split('\t')
        c = 0
        tmpJson = {}

        for val in sl:
            if helpers.is_json(val):
                tmpJson[head[c]] = json.loads(val.strip())
            else:
                tmpJson[head[c]] = val.strip()
            c += 1
        if tmpJson["event_json"]["eventData"]:
            tmpJson["event_json"]["eventData"] = json.loads(tmpJson["event_json"]["eventData"])

        if tmpJson['platform'] == "iPhone Simulator" or tmpJson['platform'] == "iPad Simulator" or tmpJson['server_environment'] != 'prod':
            continue

        # if tmpJson['server_environment'] == 'prod' :
        col.insert(tmpJson)
        count += 1
        helpers.printProgress(count,total)

def testur():
    print ("lol")

if __name__ == "__main__":
    main()
