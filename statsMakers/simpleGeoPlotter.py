from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import helpers
import argparse
import os

def main(sessDB='sessionsNew',show=False,save=False):
    m = makeNorwayMap()
    plotOnMap(m,sessDB,'Norway',show=show,save=save)

    m = makeWorldMap()
    plotOnMap(m,sessDB,'world',show=show,save=save)


def plotOnMap(m,sessDB,name,show=False,save=False):
    sessCol = helpers.getCollection(sessDB)
    locations = sessCol.distinct('event_data.location')
    c = 0
    newC = 0
    for location in locations:
        try:
            latlon = location.split(',')
            if len(latlon) == 2:
                lat = latlon[0]
                lon = latlon[1]
                x,y = m(lon,lat)
                m.plot(x, y, 'bo', markersize=4)
        except:
            newC += 1
        c += 1
    print (newC)
    plt.ylabel('')
    plt.xlabel('')

    if save:
        location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/simpleGeoPlot" + name + ".png"
        plt.savefig(location)
        print ("Simple geo plot written to: %s" % location)
    if show:
        plt.show()

def makeWorldMap():
    m = Basemap(projection='robin', lat_0=0, lon_0=10,resolution='l', area_thresh=1000.0)

    m.drawcoastlines()
    m.drawmapboundary(fill_color='aqua')
    m.fillcontinents(color='coral',lake_color='aqua')
    return m

def makeNorwayMap():
    m = Basemap(width=3000000,height=2700000,projection='lcc',resolution='c',lat_1=25.,lat_2=25,lat_0=66,lon_0=10.)
    # oslo 59° 55' 0" North, 10° 45' 0"

    m.drawcoastlines()
    m.drawmapboundary(fill_color='aqua')
    m.fillcontinents(color='coral',lake_color='aqua')
    return m

if __name__ == "__main__":
    main()
