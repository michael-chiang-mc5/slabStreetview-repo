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


def write_csv_bob():
    """
    Write text file after high-priority data has been downloaded
    """

    with open('media/matt_black-owned-business_input.csv') as csv_input , open('media/matt-black-owned-business_ctpn.csv', 'w') as csv_output, open('media/matt-black-owned-business_googleOCR.csv', 'w') as csv_output2:
        reader = csv.DictReader(csv_input)
        # set up ctpn csv output
        fieldnames = ['ctpn_pk','boundingBox','image_url','overlay_url','black_owned_business_address']
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        # swet up googleOCR csv output
        fieldnames2 = ['pk', 'googleOCR_pk', 'image_url', 'image_fov', 'boundingBox', 'locale', 'text', 'heading', 'longitude', 'latitude', \
                       'address','overlay_url','ctpn_pk','lon_projectedLine','lat_projectedLine','AIN']
        writer2 = csv.DictWriter(csv_output2, fieldnames=fieldnames2, delimiter='\t')
        writer2.writeheader()



        for row in reader:
            bob_address = row['Address'] + ', ' + row['City'] + ', ' + row['State']
            if row['City']!='Los Angeles':
                continue
            print(bob_address)
            address_str = bob_address.replace(' ','+')
            lnglat = geocode(address_str)
            if lnglat is False:
                print('geocode of '+address_str+' failed')
                continue
            mapPoints = filter_db(lnglat)

            for mapPoint in mapPoints:
                boundingBoxes = mapPoint.get_CTPN_boundingBoxes()
                for boundingBox in boundingBoxes:
                    if boundingBox.is_nil:
                        continue
                    writer.writerow({'ctpn_pk': boundingBox.pk, \
                                     'boundingBox': [boundingBox.x1, boundingBox.x2, boundingBox.y1, boundingBox.y2], \
                                     'image_url': boundingBox.streetviewImage.image_url(), \
                                     'overlay_url': 'http://104.131.145.75/ImagePicker/overlayBox/%d/%d/%d/%d/%d' % (boundingBox.streetviewImage.pk,boundingBox.x1, boundingBox.x2, boundingBox.y1, boundingBox.y2) , \
                                     'black_owned_business_address': bob_address, \
                                     })

                googleOCRs = mapPoint.get_GoogleOCR()
                for googleOCR in googleOCRs:
                    words = googleOCR.naive_words()
                    for word in words:
                        boundingBoxes = BoundingBox.objects.filter(streetviewImage=googleOCR.streetviewImage)
                        ctpn_pk = 'na'
                        for boundingBox in boundingBoxes:
                            overlap = overlappingBoundingBox(word['boundingBox'],[boundingBox.x1, boundingBox.x2, boundingBox.y1, boundingBox.y2])
                            if overlap:
                                ctpn_pk = boundingBox.pk
                                break

                        lat_projectedLine, lon_projectedLine, angle_projectedLine = calculate_projected_line(googleOCR.streetviewImage.fov * 3,word['boundingBox'],googleOCR.streetviewImage.heading,googleOCR.streetviewImage.mapPoint.latitude,googleOCR.streetviewImage.mapPoint.longitude)
                        lat_camera = googleOCR.streetviewImage.mapPoint.latitude
                        lon_camera = googleOCR.streetviewImage.mapPoint.longitude
                        AIN = get_intersecting_AIN(lat_camera,lon_camera,lat_projectedLine,lon_projectedLine)

                        writer2.writerow({
                                         'googleOCR_pk':   googleOCR.pk, \
                                         'image_url':       googleOCR.streetviewImage.image_url(), \
                                         'image_fov':       googleOCR.streetviewImage.fov * 3, \
                                         'boundingBox':    word['boundingBox'], \
                                         'locale':         word['locale'], \
                                         'text':         word['text'], \
                                         'heading':      googleOCR.streetviewImage.heading, \
                                         'longitude':    googleOCR.streetviewImage.mapPoint.longitude, \
                                         'latitude':    googleOCR.streetviewImage.mapPoint.latitude, \
                                         'address':     googleOCR.streetviewImage.mapPoint.address, \
                                         'overlay_url': 'http://104.131.145.75/ImagePicker/overlayBox/%d/%d/%d/%d/%d' % (googleOCR.streetviewImage.pk,word['boundingBox'][0], word['boundingBox'][1], word['boundingBox'][2], word['boundingBox'][3]) , \
                                         'ctpn_pk':     ctpn_pk, \
                                         'lat_projectedLine': lat_projectedLine, \
                                         'lon_projectedLine': lon_projectedLine, \
                                         'AIN': AIN, \
                                        })

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


def generate_signs():
    print(GoogleOCR.objects.count(),' total googleOCR results')
#    for googleOCR in GoogleOCR.objects.all().iterator():
#        print('generating signs for googleOCR=',googleOCR.pk)
#        googleOCR.generate_signs() # 97505
    print("starting")
    Sign.objects.all().delete()
    print("Signs deleted")

    pks = list(GoogleOCR.objects.all().order_by('pk').values_list('pk',flat=True))

    for pk in pks:
        g = GoogleOCR.objects.get(pk=pk)
        googleOCR.generate_signs()




def write_csv_sign(box,name):

    if box == 'all':
        signs = Sign.objects.all()
    else:
        lon1 = box['lon1']
        lon2 = box['lon2']
        lat1 = box['lat1']
        lat2 = box['lat2']
        signs = Sign.objects.filter(boundingBox__streetviewImage__mapPoint__longitude__gte=min(lon1,lon2)) \
                            .filter(boundingBox__streetviewImage__mapPoint__longitude__lte=max(lon1,lon2)) \
                            .filter(boundingBox__streetviewImage__mapPoint__latitude__gte=min(lat1,lat2)) \
                            .filter(boundingBox__streetviewImage__mapPoint__latitude__lte=max(lat1,lat2))

    with open('media/'+name+'_signs.csv', 'w',50) as csv_output:
        # set up ctpn csv output
        fieldnames = ['overlay_oneBox' , 'overlay_allBoxes', \
                      'text', 'longitude', 'latitude', 'address', 'AIN', 'distance_to_AIN', \
                      'language_worddist=0','language_worddist=1' \
                     ]

        writer = csv.DictWriter(csv_output, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()

        for sign in signs:
            print(sign.text)
            writer.writerow({
                             'overlay_oneBox': 'http://104.131.145.75:8888/ImagePicker/overlayBox/%d/%d/%d/%d/%d/' % (sign.boundingBox.streetviewImage.pk,sign.boundingBox.x1, sign.boundingBox.x2, sign.boundingBox.y1, sign.boundingBox.y2) , \
                             'overlay_allBoxes': 'http://104.131.145.75:8888/ImagePicker/listImage/%d/' % (sign.boundingBox.streetviewImage.pk), \
                             'text':         sign.text.replace("\t","_").replace(",","_").replace(" ","_"), \
                             'longitude':   sign.boundingBox.streetviewImage.mapPoint.longitude, \
                             'latitude':    sign.boundingBox.streetviewImage.mapPoint.longitude, \
                             'address':     sign.boundingBox.streetviewImage.mapPoint.address.replace("\t","_").replace(",","_").replace(" ","_"), \
                             'AIN': sign.AIN(), \
                             'distance_to_AIN': sign.distance_to_AIN(), \
                             'language_worddist=1': sign.language(), \
                             'language_worddist=0': sign.language(match_threshold=0) \
                            })






def write_csv_parcelVsLanguage(box,name):
    lang = ['ko','en','es','th','zh']

    if box == 'all':
        signs = Sign.objects.all()
        ains = Sign.objects.all().values_list('boundingBox__AIN',flat=True).distinct()
        ains = list(ains)
        ains.remove(None)
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


    with open('media/'+name+'_parcelVsLanguage.csv', 'w') as csv_output:
        fieldnames = ['AIN'] + lang
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()

        count = 0
        for ain in ains:
            signs = Sign.objects.filter(boundingBox__AIN=ain)

            # initialize dictionary to count lanagues
            d = {'AIN':ain}
            for l in lang:
                d[l] = 0

            # count languages in signs
            for sign in signs:
                languages = sign.language()
                languages = languages.split(',')
                for l in languages:
                    for l2 in lang:
                        if l==l2:
                            d[l] = d[l] + 1

            # write row
            count = count + 1
            print(d, ' , ', count, '/', len(ains), ' complete')
            writer.writerow(d)





def write_csv_julia(box,name):
    lon1 = box['lon1']
    lon2 = box['lon2']
    lat1 = box['lat1']
    lat2 = box['lat2']
    mapPoints = MapPoint.objects.filter(longitude__gte=min(lon1,lon2)).filter(longitude__lte=max(lon1,lon2)).filter(latitude__gte=min(lat1,lat2)).filter(latitude__lte=max(lat1,lat2))

    with open('media/'+name+'_ctpn.csv', 'w') as csv_output, open('media/'+name+'_googleOCR.csv', 'w') as csv_output2:
        # set up ctpn csv output
        fieldnames = ['ctpn_pk','boundingBox','image_url','overlay_url']
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        # swet up googleOCR csv output
        fieldnames2 = ['pk', 'googleOCR_pk', 'image_url', 'image_fov', 'boundingBox', 'locale', 'text', 'heading', 'longitude', \
                       'latitude', 'address','overlay_url','ctpn_pk', 'lon_projectedLine', 'lat_projectedLine', 'AIN']
        writer2 = csv.DictWriter(csv_output2, fieldnames=fieldnames2, delimiter='\t')
        writer2.writeheader()

        for mapPoint in mapPoints:
            boundingBoxes = mapPoint.get_CTPN_boundingBoxes()
            for boundingBox in boundingBoxes:
                if boundingBox.is_nil:
                    continue
                writer.writerow({'ctpn_pk': boundingBox.pk, \
                                 'boundingBox': [boundingBox.x1, boundingBox.x2, boundingBox.y1, boundingBox.y2], \
                                 'image_url': boundingBox.streetviewImage.image_url(), \
                                 'overlay_url': 'http://104.131.145.75/ImagePicker/overlayBox/%d/%d/%d/%d/%d' % (boundingBox.streetviewImage.pk,boundingBox.x1, boundingBox.x2, boundingBox.y1, boundingBox.y2) , \
                                 })

            googleOCRs = mapPoint.get_GoogleOCR()
            for googleOCR in googleOCRs:
                words = googleOCR.naive_words()
                for word in words:
                    boundingBoxes = BoundingBox.objects.filter(streetviewImage=googleOCR.streetviewImage)
                    ctpn_pk = 'na'
                    for boundingBox in boundingBoxes:
                        overlap = overlappingBoundingBox(word['boundingBox'],[boundingBox.x1, boundingBox.x2, boundingBox.y1, boundingBox.y2])
                        if overlap:
                            ctpn_pk = boundingBox.pk
                            break

                    lat_projectedLine, lon_projectedLine, angle_projectedLine = calculate_projected_line(googleOCR.streetviewImage.fov * 3,word['boundingBox'],googleOCR.streetviewImage.heading,googleOCR.streetviewImage.mapPoint.latitude,googleOCR.streetviewImage.mapPoint.longitude)
                    lat_camera = googleOCR.streetviewImage.mapPoint.latitude
                    lon_camera = googleOCR.streetviewImage.mapPoint.longitude
                    AIN = get_intersecting_AIN(lat_camera,lon_camera,lat_projectedLine,lon_projectedLine)


                    writer2.writerow({
                                     'googleOCR_pk':   googleOCR.pk, \
                                     'image_url':       googleOCR.streetviewImage.image_url(), \
                                     'image_fov':       googleOCR.streetviewImage.fov * 3, \
                                     'boundingBox':    word['boundingBox'], \
                                     'locale':         word['locale'], \
                                     'text':         word['text'].replace(' ','_'), \
                                     'heading':      googleOCR.streetviewImage.heading, \
                                     'longitude':    googleOCR.streetviewImage.mapPoint.longitude, \
                                     'latitude':    googleOCR.streetviewImage.mapPoint.latitude, \
                                     'address':     googleOCR.streetviewImage.mapPoint.address, \
                                     'overlay_url': 'http://104.131.145.75/ImagePicker/overlayBox/%d/%d/%d/%d/%d' % (googleOCR.streetviewImage.pk,word['boundingBox'][0], word['boundingBox'][1], word['boundingBox'][2], word['boundingBox'][3]) , \
                                     'ctpn_pk':     ctpn_pk, \
                                     'lat_projectedLine': lat_projectedLine, \
                                     'lon_projectedLine': lon_projectedLine, \
                                     'AIN': AIN, \
                                    })


def set_priority_bob():
    """
    Marks mapPoints high-priority based on Matt's dataset on black-owned business
    """
    csv_file = 'media/matt_black-owned-business.csv'
    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            address_str = row['Address'] + ', ' + row['City'] + ', ' + row['State']
            if row['City']!='Los Angeles':
                continue
            print(address_str)
            #print(len(BoundingBox.objects.all()))
            address_str = address_str.replace(' ','+')

            lnglat = geocode(address_str)

            if lnglat is False:
                print('geocode of '+address_str+' failed')
                continue
            mapPoints = filter_db(lnglat)
            set_priority_mapPoints(mapPoints)

    # number of high_priority mapPoints
    mapPoints = MapPoint.objects.filter(high_priority=True)
    print("There are ", len(mapPoints), " total high-priority mapPoints")



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
