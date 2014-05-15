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
    drawCirclesAndStuff(uniqueSessions)
    # pydottestur(uniqueSessions)

def groupSessions(uniqueSessions):
    sessions = groupSessionsForUsers()
    for session in sessions:
        sorted_events = sortEventsOnTimeStamp(session['events'])
        checkIfSessionMatchWithSessions([x[1] for x in sorted_events],uniqueSessions)


# def pydottestur(uniqueSessions):
#     graph = pydot.Dot(graph_type='digraph')
#     start_node = pydot.Node("Start", style="filled", fillcolor="red")

#     app_started_node = pydot.Node('app_started')
#     user_logged_in_node = pydot.Node('user_logged_in')

#     product_wanted_node = pydot.Node('product_wanted')
#     product_detail_clicked_node = pydot.Node('product_detail_clicked')
#     storefront_clicked_node = pydot.Node('storefront_clicked')
#     activity_clicked_node = pydot.Node('activity_clicked')
#     around_me_clicked_node = pydot.Node('around_me_clicked')
#     featured_storefront_clicked_node = pydot.Node('featured_storefront_clicked')
#     friend_invited_node = pydot.Node('friend_invited')
#     stores_map_clicked_node = pydot.Node('stores_map_clicked')
#     product_purchase_intended_node = pydot.Node('product_purchase_intended')
#     store_clicked_node = pydot.Node('store_clicked')
#     featured_collection_clicked_node = pydot.Node('featured_collection_clicked')


#     graph.add_node(app_started_node)
#     graph.add_node(user_logged_in_node)
#     graph.add_node(product_wanted_node)
#     graph.add_node(product_detail_clicked_node)
#     graph.add_node(storefront_clicked_node)
#     graph.add_node(activity_clicked_node)
#     graph.add_node(around_me_clicked_node)
#     graph.add_node(featured_storefront_clicked_node)
#     graph.add_node(friend_invited_node)
#     graph.add_node(stores_map_clicked_node)
#     graph.add_node(product_purchase_intended_node)
#     graph.add_node(store_clicked_node)
#     graph.add_node(featured_collection_clicked_node)

#     for session in uniqueSessions:
#         prevEvent = ''
#         for event in session:
#             edge = pydot.Edge(node_d, node_a)
#             edge.set_label("and back we go again")
#             edge.set_labelfontcolor("#009933")
#             edge.set_fontsize("10.0")
#             edge.set_color("blue")
#             print (edge.get_label())
#             sys.exit()
#             if prevEvent == '':
#                 # dot.node('B', event)
#                 edges.append('A')
#             prevEvent = event
#             print ()

#     # and finally we create the edges
#     # to keep it short, I'll be adding the edge automatically to the graph instead
#     # of keeping a reference to it in a variable
#     graph.add_edge(pydot.Edge(node_a, node_b))
#     graph.add_edge(pydot.Edge(node_b, node_c))
#     graph.add_edge(pydot.Edge(node_c, node_d))
#     # but, let's make this last edge special, yes?
#     graph.add_edge(pydot.Edge(node_d, node_a, label="and back we go again", labelfontcolor="#009933", fontsize="10.0", color="blue"))

# # and we are done
# graph.write_png('example2_graph.png')


def drawCirclesAndStuff(uniqueSessions):
    dot = Digraph(comment='Session-pattern')
    dot.node('A', 'Start')
    dot.node('B', 'app_started')
    dot.node('C', 'user_logged_in')

    dot.node('D', 'storefront_clicked')
    dot.node('E', 'product_detail_clicked')
    dot.node('F', 'product_wanted')
    dot.node('G', 'activity_clicked')
    dot.node('H', 'around_me_clicked')
    dot.node('I', 'featured_storefront_clicked')
    dot.node('J', 'friend_invited')
    dot.node('K', 'stores_map_clicked')
    dot.node('L', 'product_purchase_intended')
    dot.node('M', 'store_clicked')
    dot.node('N', 'featured_collection_clicked')

    edges = {}
    # {form:node, to:node, count:count}
    for session in uniqueSessions:
        prevNode = ''
        for event in session['session']:
            node = nodeMapper(event)
            fromTo = ''
            if prevNode == '':
                fromTo = 'A' + node
            else:
                fromTo = prevNode + node
            addEdgeToEdges(fromTo,edges)
            prevNode = nodeMapper(event)

    edges_sorted = sorted(edges.items(), key=operator.itemgetter(1))
    print (edges_sorted)
    for edge in edges_sorted:
        dot.edge(edge[0], edge[1], constraint='true', label=str(edges[edge]))

    # print(dot.source)
    dot.render('test-output/round-table.gv', view=False)

def addEdgeToEdges(fromTo,edges):
    if fromTo in edges:
        edges[fromTo] += 1
    else:
        edges[fromTo] = 1

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
