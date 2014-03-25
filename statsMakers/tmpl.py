import sys
import argparse
import helpers
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Construct Training, Validation and Prediction files from mongoDB.')
parser.add_argument('-sc', type=str, default="sessions")
parser.add_argument('-c', type=str, default="outMF.csv")
args = parser.parse_args()

sessCol = helpers.getCollection(args.sc)

print ("Collection used: ", args.sc)
print ("Output file:     ", args.c)
print ("")

total = 0

def main():
    #Do something awesome

    total = len()
    count = 0

    helpers.printProgress(count,total)

if __name__ == "__main__":
    main()
