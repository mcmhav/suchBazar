#! /usr/bin/python
# import numpy as np
# from mpl_toolkits.basemap import Basemap
# import matplotlib.pyplot as plt
# from datetime import datetime
# # miller projection
# map = Basemap(projection='mill',lon_0=180)
# # plot coastlines, draw label meridians and parallels.
# map.drawcoastlines()
# map.drawparallels(np.arange(-90,90,30),labels=[1,0,0,0])
# map.drawmeridians(np.arange(map.lonmin,map.lonmax+30,60),labels=[0,0,0,1])
# # fill continents 'coral' (with zorder=0), color wet areas 'aqua'
# map.drawmapboundary(fill_color='aqua')
# map.fillcontinents(color='coral',lake_color='aqua')
# # shade the night areas, with alpha transparency so the
# # map shows through. Use current time in UTC.
# date = datetime.utcnow()
# CS=map.nightshade(date)
# plt.title('Day/Night Map for %s (UTC)' % date.strftime("%d %b %Y %H:%M:%S"))
# plt.show()

import matplotlib
matplotlib.use('Qt4Agg')
from datetime import datetime
import os
DIR = 'data/'

dirList=os.listdir(DIR)

unzip = lambda l:tuple(zip(*l))

all_dates = {}
for fname in dirList:
    if fname.startswith('gootz-access'):
        counts = {}
        d = datetime.strptime(fname.split('.')[1], '%Y-%m-%d')
        with open(DIR+fname) as f:
            data = f.readlines()
            for line in data:
                if line.find('err/version') != -1:
                    addr = line.split('-')[0].strip()
                    if counts.has_key(addr):
                        counts[addr] += 1
                    else:
                        counts[addr] = 1
        all_dates[d] = counts

sorted_dates = sorted(all_dates.keys())

import GeoIP
gi = GeoIP.open('GeoLiteCity.dat',GeoIP.GEOIP_STANDARD)

insts_pos = {}
devs_pos = {}

for date in sorted_dates:
    for ip, count in all_dates[date].iteritems():
        record = gi.record_by_name(ip)
        if record and record['latitude']:
            lon = record['longitude']
            lat = record['latitude']

            toinc = devs_pos if count > 5 else insts_pos
            if toinc.has_key((lon,lat)):
                toinc[(lon,lat)] += 1
            else:
                toinc[(lon,lat)] = 1

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
# lon_0 is central longitude of robinson projection.
# resolution = 'c' means use crude resolution coastlines.
m = Basemap(projection='robin',lon_0=0,resolution='c')
#set a background colour
m.drawmapboundary(fill_color='#85A6D9')
# draw coastlines, country boundaries, fill continents.
m.fillcontinents(color='white',lake_color='#85A6D9')
m.drawcoastlines(color='#6D5F47', linewidth=.4)
m.drawcountries(color='#6D5F47', linewidth=.4)
# draw lat/lon grid lines every 30 degrees.
m.drawmeridians(np.arange(-180, 180, 30), color='#bbbbbb')
m.drawparallels(np.arange(-90, 90, 30), color='#bbbbbb')

inst_lngs = [entry[0][0] for entry in insts_pos.iteritems()]
inst_lats = [entry[0][1] for entry in insts_pos.iteritems()]
inst_count = [entry[1] for entry in insts_pos.iteritems()]
inst_x,inst_y = m(inst_lngs,inst_lats)

s_inst_count = [p * p for p in inst_count]
m.scatter(
    inst_x,
    inst_y,
    s=s_inst_count, #size
    c='blue', #color
    marker='o', #symbol
    alpha=0.25, #transparency
    zorder = 2, #plotting order
    )
for population, xpt, ypt in zip(inst_count, inst_x, inst_y):
    label_txt = int(round(population, 0)) #round to 0 dp and display as integer
    plt.text(
        xpt,
        ypt,
        label_txt,
        color = 'blue',
        size='small',
        horizontalalignment='center',
        verticalalignment='center',
        zorder = 3,
        )

devs_lngs = [entry[0][0] for entry in devs_pos.iteritems()]
devs_lats = [entry[0][1] for entry in devs_pos.iteritems()]
devs_count = [entry[1] for entry in devs_pos.iteritems()]
devs_x,devs_y = m(devs_lngs,devs_lats)

s_devs_count = [p * p for p in devs_count]
m.scatter(
    devs_x,
    devs_y,
    s=s_devs_count, #size
    c='red', #color
    marker='o', #symbol
    alpha=0.25, #transparency
    zorder = 4, #plotting order
    )
for population, xpt, ypt in zip(devs_count, devs_x, devs_y):
    label_txt = int(round(population, 0)) #round to 0 dp and display as integer
    plt.text(
        xpt,
        ypt,
        label_txt,
        color = 'red',
        size='small',
        horizontalalignment='center',
        verticalalignment='center',
        zorder = 5,
        )


#add a title and display the map on screen
plt.title('From where Err is used.')
plt.show()
