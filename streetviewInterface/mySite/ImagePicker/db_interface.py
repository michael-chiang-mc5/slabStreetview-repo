# This file contains functionality to generate csv files for:
#   - Matt's black-owned business project
#   -
import csv
from django.conf import settings
import urllib.request, json, requests
from .models import *
import math
from .FindAngle_aradya import calculate_projected_line
from .parcel_boundary_helper import get_intersecting_AIN

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

# bb = [x1,x2,y1,y2]
def overlappingBoundingBox(bb1,bb2):
    x1 = bb1[0]
    x2 = bb1[1]
    y1 = bb1[2]
    y2 = bb1[3]
    xx1 = bb2[0]
    xx2 = bb2[1]
    yy1 = bb2[2]
    yy2 = bb2[3]

    if x1 > xx2:
        return False
    elif x2 < xx1:
        return False
    elif y1 > yy2:
        return False
    elif y2 < yy1:
        return False
    else:
        return True



def set_priority_fromJuliaBuffer():
    with open('media/MapPoints_0425.csv') as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)
        for i in reader:
            pk = i[1]
            print(i)
            mapPoint = MapPoint.objects.get(pk=pk)
            mapPoint.high_priority = True
            mapPoint.save()


def set_priority():
    mapPoints = MapPoint.objects.all()

    print('num high priority mapPoint = ', mapPoints.filter(high_priority=True).count())

    count = 0
    for mapPoint in mapPoints:
        zone = mapPoint.get_zone_code(simple=True)
        if zone == 'C':
            isComplete = mapPoint.complete()[0]
            if isComplete:
                print(mapPoint.pk, 'complete')
            else:
                print(mapPoint.pk, 'incomplete')
                count = count + 1
                if count > 184066: # 184066
                    break
                mapPoint.high_priority = not isComplete
                mapPoint.save()

    #maptags = MapTag.objects.all()
    #print(maptags[0])
    #print(maptags[0].simple_zonecode())

def set_priority_julia(box):
    """
    Marks mapPoints high priority based on whether they are within bounding box
    Ex:
        lon1 = -118.3100831509
        lat1 = 34.0634478683
        lon2 = -118.2936894894
        lat2 = 34.0637256166
    """
    lon1 = box['lon1']
    lon2 = box['lon2']
    lat1 = box['lat1']
    lat2 = box['lat2']
    print('num high priority ', MapPoint.objects.filter(high_priority=True).count())
    mapPoints = MapPoint.objects.filter(longitude__gte=min(lon1,lon2)).filter(longitude__lte=max(lon1,lon2)).filter(latitude__gte=min(lat1,lat2)).filter(latitude__lte=max(lat1,lat2))
    print('num mapPoints in bb = ', len(mapPoints))
    set_priority_mapPoints(mapPoints)
    print('num high priority ', MapPoint.objects.filter(high_priority=True).count())


def generate_signs(fresh=False):
    print("starting")
    if fresh:
        Sign.objects.all().delete()
        GoogleOCR.objects.all().update(signs_generated=False)
        print("Signs deleted")

    print("getting pk")
    pks = list(GoogleOCR.objects.all().order_by('pk').values_list('pk',flat=True))
    for pk in pks:
        g = GoogleOCR.objects.get(pk=pk)
        print('googleOCR pk = ', g.pk)
        g.generate_signs()



def write_csv_parcelVsLanguage_deprecated(box,name):
    lang = ['ko','en','es','th','zh']

    if box == 'all':
        signs = Sign.objects.all()
        ains = Sign.objects.all().values_list('boundingBox__AIN',flat=True).distinct()
        ains = list(ains)
        try:
            ains.remove(None)
        except:
            print('no nones in list')
        ains = sorted(ains)
    else:
        lon1 = box['lon1']
        lon2 = box['lon2']
        lat1 = box['lat1']
        lat2 = box['lat2']
        boundingBoxes = BoundingBox.objects.filter(streetviewImage__mapPoint__longitude__gte=min(lon1,lon2)) \
                            .filter(streetviewImage__mapPoint__longitude__lte=max(lon1,lon2)) \
                            .filter(streetviewImage__mapPoint__latitude__gte=min(lat1,lat2)) \
                            .filter(streetviewImage__mapPoint__latitude__lte=max(lat1,lat2))
        ains = boundingBoxes.values_list('AIN',flat=True).distinct()
        ains = list(ains)
        ains.remove(None)

    print(ains)

    signs = Sign.objects.filter(boundingBox__AIN__isnull=False).order_by('boundingBox__AIN')
    count = 0

    with open('media/'+name+'_parcelVsLanguage.csv', 'w', 10) as csv_output:
        fieldnames = ['AIN'] + lang
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()

        for ain in ains:

            # initialize dictionary to count lanagues
            d = {'AIN':ain}
            for l in lang:
                d[l] = 0

            # count languages in signs
            for idx in range(count,len(signs)):
                sign = signs[idx]
                print(idx, ain, sign.AIN())

                if sign.AIN() != ain:
                    break
                count += 1

                languages = sign.language(match_threshold=0)
                languages = languages.split(',')
                for l in languages:
                    for l2 in lang:
                        if l==l2:
                            d[l] = d[l] + 1

            # write row
            print(d)
            writer.writerow(d)




def write_csv_parcelVsLanguage():
    # these are the languages we can detect, should match sign.language()
    possible_codes = ['ko','zh','th','ja','zh_TW','vi','te','ta','so','pa','he','ar','fa','hy','en','es','unknown']

    # get unique ain values
    with open('media/all_signs.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        next(spamreader, None)  # skip the headers
        unique_ain = set()
        for row in spamreader:
            ain = row[8]
            unique_ain.add(ain)

    # initiate storage dictionary
    out = {}
    for ain in unique_ain:
        language_count = {}
        for code in possible_codes:
            language_count[code] = 0
        out[str(ain)] = language_count

    # get unique ain values
    with open('media/all_signs.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        next(spamreader, None)
        for row in spamreader:
            ain = row[8]
            langs = row[10]
            langs = langs.split(',')
            for lang in langs:
                out[ain][lang] += 1


    with open('media/all_parcelVsLanguage.csv', 'w', 10) as csv_output:
        fieldnames = ['AIN'] + possible_codes
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()

        for ain,langs in out.items():
            langs['AIN'] = ain
            writer.writerow(langs)




def write_csv_final(name):
    signs = Sign.objects.all()
    num_signs = signs.count()

    with open('media/'+name+'_signs.csv', 'w', 10) as csv_output:


        # set up ctpn csv output
        fieldnames = ['sign_pk','image_url', 'boundingBox','text', 'longitude','latitude', 'address','overlay_url', 'AIN', 'distance_to_AIN','language_dist=0']
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()

        count = 0
        for sign in signs:
            streetviewImage = sign.streetviewImage
            box = [sign.x1, sign.x2, sign.y1, sign.y2]
            ain = sign.AIN

            writer.writerow({
                             'sign_pk':         sign.pk, \
                             'image_url':       sign.image_url(), \
                             'boundingBox':    box, \
                             'text':         sign.text, \
                             'longitude':    streetviewImage.mapPoint.longitude, \
                             'latitude':     streetviewImage.mapPoint.latitude, \
                             'address':      streetviewImage.mapPoint.address, \
                             'overlay_url': 'http://104.131.145.75:8888/ImagePicker/overlayBox/%d/%d/%d/%d/%d' % (streetviewImage.pk,box[0], box[1], box[2], box[3]) , \
                             'AIN': ain, \
                             'distance_to_AIN': sign.distance_to_AIN, \
                             'language_dist=0': sign.language(match_threshold=0), \
                            })

            count += 1
            print("sign.pk = " ,sign.pk, '    ,    %=',count,'/',num_signs)





def set_priority_mapPoints(mapPoints):
    """
    set mapPoint priority to high if the underlying data (CTPN, images, googleOCR)
    is not complete
    """
    for mapPoint in mapPoints:
        #print("working on mapPoint.pk = " + str(mapPoint.pk))
        mapPoint_complete = mapPoint.complete()
        mapPoint.high_priority = not mapPoint_complete
        mapPoint.save()
        #print("high_priority=", mapPoint.high_priority)




# returns a dictionary with {'lng', 'lat'} of input address
def geocode(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (address,settings.GOOGLE_GEOCODE_API_KEY)
    #print(url)
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
