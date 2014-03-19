from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import helpers
import argparse

parser = argparse.ArgumentParser(description='Plot geolocations from data on map.')
parser.add_argument('-sc', type=str, default="sessions")
args = parser.parse_args()

sessCol = helpers.getCollection(args.sc)

print ("Collection used: ", args.sc)
print ("")

def main():
    m = makeMap()

    plotOnMap(m)

    plt.show()

def plotOnMap(m):
    locations = sessCol.distinct('event_data.location')
    for location in locations:
        latlon = location.split(',')
        if len(latlon) == 2:
            lat = latlon[0|bo', markersize=6)


def makeMap():
    m = Basemap(width=3000000,height=2700000,projection='lcc',
                resolution='c',lat_1=25.,lat_2=25,lat_0=66,lon_0=10.)
    # oslo 59° 55' 0" North, 10° 45' 0"

    m.drawcoastlines()
    m.drawmapboundary(fill_color='aqua')
    m.fillcontinents(color='coral',lake_color='aqua')
    return m

if __name__ == "__main__":
    main()
