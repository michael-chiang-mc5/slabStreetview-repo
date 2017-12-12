# This file contains functionality to generate csv files for:
#   - Matt's black-owned business project
#   -
import csv
from django.conf import settings
import urllib.request, json, requests
from .models import *
import math


# degrees to radians
def deg2rad(degrees):
    return math.pi*degrees/180.0
# radians to degrees
def rad2deg(radians):
    return 180.0*radians/math.pi
# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]
# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )
# Bounding box surrounding the point at given coordinates,
# assuming local approximation of Earth surface as a sphere
# of radius given by WGS84
def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    lat = deg2rad(latitudeInDegrees)
    lon = deg2rad(longitudeInDegrees)
    halfSide = 1000*halfSideInKm
    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*math.cos(lat)
    latMin = lat - halfSide/radius
    latMax = lat + halfSide/radius
    lonMin = lon - halfSide/pradius
    lonMax = lon + halfSide/pradius
    return (rad2deg(latMin), rad2deg(lonMin), rad2deg(latMax), rad2deg(lonMax))




def temp():
    csv_file = '/home/michaelc/dev/slabStreetview-repo/streetviewInterface/mySite/media/matt_black-owned-business.csv'
    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            address_str = row['Address'] + ', ' + row['City'] + ', ' + row['State']
            if row['City']!='Los Angeles':
                continue
            print(address_str)
            address_str = address_str.replace(' ','+')

            lnglat = geocode(address_str)

            if lnglat is False:
                print('geocode of '+address_str+' failed')
                continue
            mapPoints = filter_db(lnglat)
            process_mapPoints(mapPoints)

    # number of high_priority mapPoints
    mapPoints = MapPoint.objects.filter(high_priority=True)
    print("There are ", len(mapPoints), " total high-priority mapPoints")



def process_mapPoints(mapPoints):
    """
    set mapPoint priority to high if the underlying data (CTPN, images, googleOCR)
    is not complete
    """
    for mapPoint in mapPoints:
        print("working on mapPoint.pk = " + str(mapPoint.pk))
        mapPoint_complete = mapPoint.complete()
        mapPoint.high_priority = not mapPoint_complete
        mapPoint.save()
        print("high_priority=", mapPoint.high_priority)
        break




# returns a dictionary with {'lng', 'lat'} of input address
def geocode(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (address,settings.GOOGLE_GEOCODE_API_KEY)
    print(url)
    response = requests.get(url)
    try:
        rn = response.json()['results'][0]['geometry']['location'] # {'lng', 'lat'}
        return rn
    except:
        return False

# finds all mappoints within XXX distance of given lnglat coordinates
def filter_db(lnglat):
    lng = lnglat['lng']
    lat = lnglat['lat']
    latmin,lonmin,latmax,lonmax = boundingBox(lat,lng,50/1000) # get bounding box for points within 50m of latlng
    box = {'lat1':latmin,'lng1':lonmin,'lat2':latmax,'lng2':lonmax}
    mapPoints = MapPoint.objects.filter(latitude__lte=box['lat2']).filter(latitude__gte=box['lat1']).filter(longitude__lte=box['lng2']).filter(longitude__gte=box['lng1'])
    return mapPoints
