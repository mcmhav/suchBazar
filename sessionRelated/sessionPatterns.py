import sys
import argparse
import helpers
from bson import Binary, Code
import subprocess
import shlex
from graphviz import Digraph
import os
import operator
# import pydot


parser = argparse.ArgumentParser(description='Users sessions.')
parser.add_argument('-sc', type=str, default="sessions")
args = parser.parse_args()

col = helpers.getCollection(args.sc)
savePath = "../../muchBazar/src/image/"

print ("Collection used: ", args.sc)
print ("")

totalRatings = {
    'product_wanted':0,
    'product_detail_clicked':0,
    'product_purchase_intended':0
}
total = 0
usersOver19 =0

PERCENTAGE_MATCH=100

def main():
    '''
        Make easy to change from "product_purchase_intended" to "product_purchased"

        Simple:
        Get users
            Get sessions
                Store session patterns
        v.1 - Count equal session patterns
        v.2 - Count similar session patterns
            80\%\ match for instance
            Issue:
                If using matching percentage, an event can match multiple sets
                    How to decide?
                        Needed?
                    How to structure? dependent on ^
            Better to use state from - to, not complete session? nono

            Store all unique sessions to match new sessions with
                Percentage match sessions with each other, keep highest percentage match?
                What are this information going to be used for?
                    Match users, similar sessions - similar users
                How to use this to predict user behavior:
                    Markov -
                        Look back, what is the most likely session events to have happened before based on session histories?
                        Predict the next event

                        What is needed for this:
                            All unique sessions.
                            Count sessions which are equal (more weight)

                        How will this be tested, how use with coming data, how can we show that this is anything useful, how can this be used with product recommendations?



        v.2.1 - Focus on purchase. Count similar session patterns
        v.2.2 - Focus on all. Count similar session patterns

        v.3 - Make statistics for next state given current
        v.3.1 - Make statistics for next state session till now

        v.4 - Hypothesis: When a users first is buying, he or she buys a lot.
            Find pattern of massbuyers
    '''

    uniqueSessions = []
    groupSessions(uniqueSessions)
    drawCirclesAndStuff(uniqueSessions,True)
    drawCirclesAndStuff(uniqueSessions,False)
    # pydottestur(uniqueSessions)
    # allInOneWithFlow(uniqueSessions)
    # drawTopSessions(uniqueSessions)


def groupSessions(uniqueSessions):
    sessions = groupSessionsForUsers()
    for session in sessions:
        sorted_events = sortEventsOnTimeStamp(session['events'])
        checkIfSessionMatchWithSessions([x[1] for x in sorted_events],uniqueSessions)

def drawTopSessions(uniqueSessions):
    uniqueSessions_sorted = sorted(uniqueSessions, key=lambda k: k['count'], reverse=True)
    tmp = uniqueSessions_sorted[2:102]

    for session in tmp:
        drawSeparateSession(session['session'],session['count'])

def allInOneWithFlow(uniqueSessions):
    topSessions = []
    # print (uniqueSessions)
    # sorted_events = sorted(uniqueSessions.items(),reverse=False)
    # for session in uniqueSessions:
    #     print (session)
    uniqueSessions_sorted = sorted(uniqueSessions, key=lambda k: k['count'], reverse=True)
    # print (uniqueSessions_sorted[:20])
    tmp = uniqueSessions_sorted[2:32]
    dot = Digraph(comment='Session-pattern')

    count = 0
    # dot.node('1', 'Start')
    # dot.node('2', 'app_started/user_logged_in')


    states = []
    states.append('Start')
    states.append('app_started/user_logged_in')
    diagram = {}
    for session in tmp:
        prevNode = 'Start'
        for event in session['session']:
            thisNode = event
            if thisNode == 'app_started' or thisNode == 'user_logged_in':
                thisNode = "app_started/user_logged_in"

            if event not in states:
                states.append(event)
                # dot.node(str(count), event)
                count += 1


            edge = prevNode + '->' + thisNode
            if edge not in diagram:
                diagram[edge] = session['count']
            else:
                diagram[edge] += session['count']

            prevNode = thisNode

    # for state in diagram:

    for edge in diagram:
        nodes = edge.split('->')

        dot.edge(
            nodes[0],
            nodes[1],
            constraint='true',
            label=str(diagram[edge]),
            # color=color,
        )

    renderDot(dot, "allInOneFlow")


    # for session in uniqueSessions_sorted[:20]:
    #     print (uniqueSessions_sorted)
        # count += 1
        # if count > 12:
        #     sys.exit()

def renderDot(dotSource, name):
    dotSource.render(savePath + name + '-gvfile', view=False)

def drawSeparateSession(session,sid):
    dot = Digraph(comment='Session' + str(sid))
    dot.node('1', 'Start')
    count = 2
    prevNode = '1'
    for event in session:
        thisNode = str(count)
        dot.node(thisNode, event)
        dot.edge(
            prevNode,
            thisNode,
            constraint='true',
            # label=str(edges[edge]),
            # color=color,
            # weight=str(ed/ges[edge]),
        )
        count += 1
        prevNode = thisNode
    renderDot(dot, 'session-' + str(sid))

def drawCirclesAndStuff(uniqueSessions,reduced):
    dot = Digraph(comment='Session-pattern')
    dot.node('A', 'Start')
    dot.node('B', 'app_started')
    dot.node('C', 'user_logged_in')

    if reduced:
        dot.node('S', 'store_accessed')
    else:
        dot.node('D', 'storefront_clicked')
        dot.node('M', 'store_clicked')
        dot.node('I', 'featured_storefront_clicked')
        dot.node('N', 'featured_collection_clicked')

    dot.node('E', 'product_detail_clicked')
    dot.node('L', 'product_purchase_intended')
    dot.node('F', 'product_wanted')

    if reduced:
        dot.node('O', 'others')
    else:
        dot.node('G', 'activity_clicked')
        dot.node('H', 'around_me_clicked')
        dot.node('J', 'friend_invited')
        dot.node('K', 'stores_map_clicked')


    edges = {}
    # {form:node, to:node, count:count}
    for session in uniqueSessions:
        prevNode = ''
        for event in session['session']:
            node = nodeMapper(event)
            if reduced:
                node = reduceMapper(node)
            fromTo = ''
            if prevNode == '':
                fromTo = 'A' + node
            else:
                fromTo = prevNode + node
            addEdgeToEdges(fromTo,edges,session['count'])
            prevNode = nodeMapper(event)
            if reduced:
                prevNode = reduceMapper(prevNode)

    edges_sorted = sorted(edges.items(), key=operator.itemgetter(1),reverse=True)

    # for edge in edges_sorted:
    #     print (edge)
    i = 0

    # skipNodes = {'J', 'H', 'G', 'K'}
    for edge in edges:
        nodeFrom = edge[0]
        color = coloMapper(nodeFrom)

        # if (nodeFrom in skipNodes) or (edge[1] in skipNodes):
        #     continue
        dot.edge(
            nodeFrom,
            edge[1],
            constraint='true',
            label=str(edges[edge]),
            color=color,
            weight=str(edges[edge]),
        )
        i += 1

    renderDot(dot, "statesInteraction" + str(reduced))

def addEdgeToEdges(fromTo,edges,count):
    if fromTo in edges:
        edges[fromTo] += 1*count
    else:
        edges[fromTo] = 1*count

def reduceMapper(event):
    return {
        'D': 'S',
        'M': 'S',
        'I': 'S',
        'N': 'S',

        'G': 'O',
        'H': 'O',
        'J': 'O',
        'K': 'O',
    }.get(event, event)

def coloMapper(node):
    return {
        'A': 'blue',
        'B': 'red',
        'C': 'green',
        'D': 'black',
        'E': 'yellow',
        'F': 'brown',
        'G': 'purple',
        'H': 'pink',
        'I': 'orange',
        'J': 'gold',
        'K': 'cyan',
        'L': 'gray',
        'M': 'indigo',
        'N': 'violet',
        'S': 'orchid',
        'O': 'purple',
    }.get(node, 'gold')

def nodeMapper(event):
    return {
        'app_started': 'B',
        'user_logged_in':'C',
        'storefront_clicked':'D',
        'product_detail_clicked':'E',
        'product_wanted':'F',
        'activity_clicked':'G',
        'around_me_clicked':'H',
        'featured_storefront_clicked':'I',
        'friend_invited':'J',
        'stores_map_clicked':'K',
        'product_purchase_intended':'L',
        'store_clicked':'M',
        'featured_collection_clicked':'N',
    }[event]

def checkIfSessionMatchWithSessions(session,uniqueSessions):
    # if session in uniqueSessions:
    #     uniqueSessions['session'] += 1
    # else:
    #     uniqueSessions['session'] = 1

    for uSession in uniqueSessions:
        # print (uSession)
        # sys.exit()
        if session == uSession['session']:
            # uniqueSessions[uSession]['count'] +=1
            uSession['count'] += 1
            return True
    tmp = {'session':session, 'count' :1}
    uniqueSessions.append(tmp)
    # uniqueSessions += tmp
    # tmp = {'session':session, 'count':1}
    # sys.exit()
    return False

def sortEventsOnTimeStamp(events):
    sorted_events = sorted(events.items(),reverse=False)
    return sorted_events

def groupSessionsForUsers():
            # result.events.push(event);
    gReducer = Code("""
        function (cur,result) {
            tmpts = (cur.ts);
            tmpev = cur.event_id;
            event = {
                ev:tmpev,
                ts:tmpts
            };
            result.events[tmpts] = tmpev;
        }
    """)

    eventGoups = col.group(
        key = {
            'user_id':1,
            'session':1,
        },
        condition = {
            # 'user_id':user,
        },
        reduce = gReducer,
        initial = {
            'events':{},
            # 'weight':0.6
        }
    )
    return eventGoups


def handle_appStarted():
    users = sessCol.distinct('user_id')

    global total
    total = len(users)
    count = 0.0

    for user in users:
        count += 1
        if user == 'NULL' or user == '':
            continue
        else:
            hadndleUser(user)
            helpers.printProgress(count,total)
    testWithMapReduce(user)
    findTotalAverageOfRatingEvents()

def hadndleUser(user):
    print (user)

    # findStoreCount(user)
    # findTop10Items(user)
    # userEvents = sessCol.find({'user_id':user})
    # avgEventsSess = avgEventPerSession(userEvents)
    # print (avgEventsSess)
    # userStart = findMin(userEvents,'ts')
    # print (userStart)
    # userLast = findMax(userEvents,'ts')
    # print (userLast)
    # avgSession = avgSessionsTime(user)
    # print (avgSession)

    # userRatings = findRatingAmountForUser(user)

def findStoreCount(user):
    print ("Finding access count for the different stores")
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = sessCol.group(
                           key={'storefront_name':1},
                           condition={'user_id':user,'storefront_name':{'$ne':'NULL'},'storefront_name':{'$ne':''}},
                           reduce=reducer,
                           initial={'count':0}
                       )
    for s in groups:
        print (s)
    return groups
def findMin(userEvents,field):
    print ("Finding Min Value for %s" % field)
    return findMinMax(userEvents,1,field)
def findMax(userEvents,field):
    print ("Finding Max Value for %s" % field)
    return findMinMax(userEvents,-1,field)
def findMinMax(userEvents,val,field):
    return userEvents.sort(field,val)[0][field]

def avgSessionsTime(user):
    print ("Finding average sessions time")
    sessions = sessCol.find({'user_id':user}).distinct('session')
    total = 0
    for session in sessions:
        sessionEvents = sessCol.find({'user_id':user,'session':session}).sort('ts',-1)
        total += sessionEvents[0]['ts'] - sessionEvents[sessionEvents.count()-1]['ts']
    return total/len(sessions)

def avgEventPerSession(userEvents):
    print("Finding average amount of events per session")
    sessions = userEvents.distinct('session')
    return userEvents.count()/len(sessions)

def findTop10Items(user):
    print ("Finding top 10 items for user")
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = sessCol.group(
                           key={'product_id':1},
                           condition={'user_id':user,'product_id':{'$ne':'NULL'}},
                           reduce=reducer,
                           initial={'count':0}
                       )
    for s in groups:
        print (s)

    return groups

def findRatingAmountForUser(user):
    # print ("Counting rating events for user")
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = sessCol.group(
                           key={'event_id':1},
                           condition={'user_id':user,'$or':[{'event_id':'product_purchase_intended'}, {'event_id':'product_wanted'},{'event_id':'product_detail_clicked'}]},
                           reduce=reducer,
                           initial={'count':0}
                       )
    totalRatings = 0
    for s in groups:
        totalRatings += s['count']
        # print (s)


    global usersOver19
    if (totalRatings > 19):
        addToRatingTotal(groups)
        usersOver19 += 1
    # sys.exit()

    return groups

def testWithMapReduce(user):
    mapper = Code(  """
                    function () {
                        if (this.event_id == 'product_purchase_intended' || this.event_id == 'product_wanted' || this.event_id == 'product_detail_clicked')
                            emit(this.user_id, 1);
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
    result = sessCol.map_reduce(mapper, reducer, "myresults")

    for r in result.find():
        print (r)

def addToRatingTotal(userRatings):
    global totalRatings
    for rating in userRatings:
        totalRatings[rating['event_id']] += int(rating['count'])

def findTotalAverageOfRatingEvents():
    print (totalRatings)
    print (usersOver19)
    # for rating in totalRatings:
    #     print (str(rating[rating]))

if __name__ == "__main__":
    main()


# 0.8961352657
# 4.6654589372
# 8.47584541063
