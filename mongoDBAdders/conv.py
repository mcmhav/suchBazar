import json
import argparse
import sys
import helpers

parser = argparse.ArgumentParser(description='Convert tab and insert to mongoDB.')
parser.add_argument('-f', type=str, default="../data/sobazar.tab")
parser.add_argument('-c', type=str, default="prod")
args = parser.parse_args()

col = helpers.getCollection(args.c,True)

print ("File used: ", args.f)
print ("Collection used: ", args.c)
print ("")

def main(dbLocation):
    if dbLocation != "":
        args.f = dbLocation
    f = open(args.f)
    # head = f.readline().strip().split('\t')
    head = getHead()

    headJson = {}
    headJson["head"] = head
    col.insert(headJson)

    lines = f.readlines()
    f.close()

    total = len(lines)
    count = 0

    for line in lines:
        tmpJson = addLineToTmp(line,head)

        # if count >= 214851:
        #     print (line)
        #     print (tmpJson)
        try:
            handleDoubleJson(tmpJson)
        except ValueError:
            print ("Oops tmpJson err")
            print (tmpJson)
            print (line)

        if isTestEvent(tmpJson):
            continue

        # if tmpJson['server_environment'] == 'prod' :
        try:
            col.insert(tmpJson)
        except ValueError:
            print ("Oops")
            print (tmpJson)
            print (line)

        count += 1
        helpers.printProgress(count,total)

    print ()
    print ((count/total)*100)
    print ("Done lol")

def isTestEvent(tmpJson):
    if 'serverEnvironment' in tmpJson['event_data']:
        return tmpJson['event_data']['serverEnvironment'] != 'prod'
    return tmpJson['platform'] == "iPhone Simulator" or tmpJson['platform'] == "iPad Simulator" or tmpJson['server_environment'] != 'prod'

def handleDoubleJson(tmpJson):
    if 'eventData' in tmpJson['event_json']:
        if tmpJson["event_json"]["eventData"] != '':
            tmpJson["event_json"]["eventData"] = json.loads(tmpJson["event_json"]["eventData"])

def addLineToTmp(line,head):
    sl = line.split('\t')
    c = 0
    tmpJson = {}

    for val in sl:
        if helpers.is_json(val):
            tmpJson[head[c]] = json.loads(val.strip())
        else:
            tmpJson[head[c]] = val.strip()
        c += 1
    return tmpJson


def getHead():
    head = [
                "service_id",
                "event_id",
                "event_data",
                "server_time_stamp",
                "tag_id",
                "user_agent",
                "storefront_position",
                "client_time_stamp",
                "storefront_name",
                "country_id",
                "price",
                "product_type",
                "product_id",
                "origin_ui",
                "tag_position",
                "gender_target",
                "user_id",
                "tag_name",
                "login_type",
                "server_environment",
                "currency",
                "age_target",
                "time_stamp",
                "storefront_id",
                "platform",
                "country_name",
                "event_location",
                "retailer_brand",
                "app_version",
                "product_name",
                "transaction_id",
                "event_json",
                "hr",
                "ts",
                "epoch_day",
                "epoch_week",
                "yr",
                "mo",
                "dy",
            ]
    return head

# useVals = {
                # "service_id",
                # "event_id",
                # "event_data",
                # "price",
                # "product_id",
                # "product_name",
                # "retailer_brand",
                # "user_agent",
                # "gender_target",
                # "storefront_position",
                # "storefront_name",
                # "storefront_id",
                # "country_id",
                # "user_id",
                # "product_type",
                # "origin_ui",
                # "tag_position",
                # "country_name",
                # "time_stamp",
                # "tag_name",
                # "login_type",
                # "event_location",
                # "tag_id",
                # "server_time_stamp",
                # "client_time_stamp",
                # "server_environment",
                # "currency",
                # "age_target",
                # "platform",
                # "app_version",
                # "transaction_id",
                # "event_json",
                # "hr",
                # "ts",
                # "epoch_day",
                # "epoch_week",
                # "yr",
                # "mo",
                # "dy",
            # }

if __name__ == "__main__":
    main("")
