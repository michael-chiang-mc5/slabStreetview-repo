from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import os
import urllib.request
from django.conf import settings

# Create your views here.
def index(request):
    context = {}
    return getHeading(request)
    #return render(request, 'ImagePicker/index4.html',context)

def listImage(request):
    #return savePoint(request)    
    streetviewImages = StreetviewImage.objects.all()
    context = {'streetviewImages':streetviewImages}
    #return HttpResponse("asdf")
    return render(request, 'ImagePicker/listImage.html',context)

# Takes POST data
# saves mapPoint
# downloads associated streetview images to point and saves streetviewImage (2 per mapPoint for right and left)
def savePoint(request):
    #url = "http://maps.googleapis.com/maps/api/streetview?size=640x640&location=42.34554965704973,-71.09832376428187&fov=90&heading=270.0&pitch=0.0&key=AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo"
    #savLoc = "/Users/mcah5a/Desktop/projects/slabStreetview-repo/streetviewInterface/mySite/media/"
    #fi = "1.jpg"
    #data = urllib.request.urlretrieve(url, os.path.join(savLoc,fi))


    latitude=42.34554965704973
    longitude=-71.09832376428187
    photographerHeading=90
    panoID="asdf"
    mapPoint = MapPoint(latitude=latitude, \
                        longitude=longitude, \
                        photographerHeading=photographerHeading, \
                        panoID=panoID)
    mapPoint.save()


    xdim = 640
    ydim = 640
    fov=90
    pitch=0
    url_left =   "http://maps.googleapis.com/maps/api/streetview?size=%dx%d&location=%f,%f&fov=%d&heading=%f&pitch=%f&key=AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo" \
                 % (xdim,ydim,latitude,longitude,fov,photographerHeading+90,pitch)

    # left image
    streetviewImage_left = StreetviewImage(mapPoint=mapPoint, \
                                           heading=photographerHeading+90, \
                                           fov=fov, \
                                           pitch=pitch)
    streetviewImage_left.save()
    fi = str(streetviewImage_left.pk) + ".jpg"
    fi_path = os.path.join(settings.MEDIA_ROOT,fi)
    data = urllib.request.urlretrieve(url_left, fi_path)
    streetviewImage_left.image = fi # this should be set with respect to MEDIA_ROOT
    streetviewImage_left.save()

    # right image TODO


    return HttpResponse(streetviewImage_left)




# Given GPS coordinates, return the heading value perpendicular to the road
def getHeading(request):
    context = {}
    return render(request, 'ImagePicker/panorama.html',context)


base = "https://maps.googleapis.com/maps/api/streetview?size=1200x800&location="
loc="457 West Robinwood Street, Detroit, Michigan 48203"
add="&key="
key="AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo"
url = base+loc+add+key
