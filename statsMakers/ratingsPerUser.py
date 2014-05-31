import datetime
import sys
import helpers
from bson import Binary, Code
import math
import numpy as np
import matplotlib.pyplot as plt
import os

def main(sessDB='sessionsNew'):
    '''
    '''
    ueic = getUserEventOnItemCounts(sessDB)
    print (ueic)

    counts = [int(x['count']) for x in ueic]
    avgCount = helpers.getAvgOfCount(counts)
    print (avgCount)

    ueic_sorted = sorted(ueic, key=lambda k: k['count'],reverse=True)
    print (ueic_sorted)


    plotRatingCounts(yaxis,xaxis,xticks,show=True)

def plotRatingCounts(yaxis,xaxis,xticks,show=False):
    '''
    '''
    helpers.makePlot(
        'ratingsPerUser',
        yaxis,
        xaxis,
        # title='Global Sessions Count',
        ylabel='Amount of Users',
        xlabel='Session count',
        show=show,
        grid=True,
        xticks=xticks
    )

def getUserEventOnItemCounts(sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        tmp = [
                            'product_purchase_intended',
                            'product_wanted',
                            'product_detail_clicked'
                        ];
                        hasProp = (tmp.indexOf(cur.event_id) > -1);
                        if (hasProp) {
                            result.count += 1
                        }
                    }
                   """)
    k = 'user_id'
    groups = col.group(
                           key={k:1},
                           condition={'$and':[
                                {k:{'$ne':'NULL'}},
                                {k:{'$ne':'N/A'}},
                                {k:{'$ne':''}}
                            ]},
                           reduce=reducer,
                           initial={'count':0}
                       )
    return groups

if __name__ == "__main__":
    main()
