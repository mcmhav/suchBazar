import csv
import argparse
import sys
import helpers
from bson import Binary, Code
from bson.son import SON
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
import matplotlib.ticker as ticker
import operator
import os

def main(sessDB='sessionsNew', writeLocation='stats/eventsPerDay'):
  eventGroups = eventsPerDay(sessDB)
  makePlot(eventGroups)

def writeEventsToFile(eventGroups):
  c = helpers.getCSVWriter(args.d + '/' + 'eventsPerDay')
  c.writerow(["Date","Events"])

  for g in eventGroups:
      print (g)
      if (g['yr'] != None):
          s = str(int(g['yr'])) + str(int(g['mo'])+10) + str(int(g['dy'])+10)
          s2 = "date: " + str(int(s) - 1010)
          # s = str(int(g['yr'])) + "." + str(g['mo']) + "." + str(g['dy'])
          c.writerow([s2,g['count']])

  helpers.closeF()

def eventsPerDay(sessDB):
  col = helpers.getCollection(sessDB)
  reducer = Code("""
                  function (cur,result) {
                      result.count += 1
                  }
                 """)

  eventGroups = col.group(
                         key={'yr':1,'mo':1,'dy':1},
                         condition={},
                         reduce=reducer,
                         initial={'count':0}
                     )
  return eventGroups

def makePlot(eventGroups):
  # datafile = cbook.get_sample_data('aapl.csv', asfileobj=False)
  # print ('loading %s' % datafile)
  # dy_s = sorted(eventGroups, cmp=lambda d,m,y: k['dy'], reverse=True)
  # mo_s = sorted(dy_s, key=lambda k: k['mo'], reverse=True)
  eventGroups_sorted = sorted(eventGroups, key=lambda elem: "%s %s %s" % (elem['yr'], elem['mo'],elem['dy']), reverse=False)

  yaxis = []
  yaxis_labels = []
  xaxis = []
  groupsAsCSV = []
  groupsAsCSV.append('date,count')
  count = 0
  for events in eventGroups_sorted:
    s = str(int(events['yr'])) + '-' + str(int(events['mo'])) + '-' + str(int(events['dy']))
    count += 1
    if count % 9 == 0:
      yaxis_labels.append(s)
      yaxis.append(count)
    xaxis.append(events['count'])

  width = 0.6
  fig, ax = plt.subplots()
  fig.set_size_inches(14.0,8.0)
  plt.axis([0, count, 0, 2500])
  print (len(yaxis_labels)*9+1)
  print (len(xaxis))
  ax.bar(range(len(yaxis_labels)*9+3), xaxis, width=width)
  ax.set_xticks(yaxis)
  ax.set_xticklabels(yaxis_labels)
  fig.autofmt_xdate()
# fig = plt.figure(figsize=(4, 5), dpi=100)
  plt.title('Events per day')
  plt.ylabel('Amount Of Events')
  plt.xlabel('Date')
  plt.grid(True)

  location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/eventsPerDay.png"
  plt.savefig(location)
  print ("Event per day written to: %s" % location)

if __name__ == "__main__":
    main()
