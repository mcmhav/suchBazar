import helpers
# import conv
import restructureEventMetadata
# import sessionCons
# import negativeRatingsForItems

def main():
    print ('Adding and handling mongoDB tasks')
    conv.main()
    restructureEventMetadata.main()
    sessionCons.main()
    negativeRatingsForItems.main()

if __name__ == "__main__":
    main()
