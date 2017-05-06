from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import os
import urllib.request

# Create your views here.
def index(request):
    context = {}
    return getHeading(request)
    #return render(request, 'ImagePicker/index4.html',context)


def listImage(request):
    #url = "http://maps.googleapis.com/maps/api/streetview?size=640x640&location=42.34554965704973,-71.09832376428187&fov=90&heading=270.0&pitch=0.0&key=AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo"
    #savLoc = "/Users/mcah5a/Desktop/projects/slabStreetview-repo/streetviewInterface/mySite/media/"
    #fi = "1.jpg"
    #data = urllib.request.urlretrieve(url, os.path.join(savLoc,fi))


    latitude=42.34554965704973
    longitude=-71.09832376428187
    photographerHeading=90
    #panoID="asdf"
    #mapPoint = MapPoint(latitude=latitude, \
    #                    longitude=longitude, \
    #                    photographerHeading=photographerHeading, \
    #                    panoID=panoID)
    #mapPoint.save()

    mapPoints = MapPoint.objects.get(pk=1)

    xdim = 640
    ydim = 640
    fov=90
    pitch=0
    url =   "http://maps.googleapis.com/maps/api/streetview?size=%dx%d&location=%f,%f&fov=%d&heading=%f&pitch=%f&key=AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo" \
            % (xdim,ydim,latitude,longitude,fov,photographerHeading+90,pitch)

    #url = "http://maps.googleapis.com/maps/api/streetview?size=640x640&location=42.34554965704973,-71.09832376428187&fov=90&heading=270.0&pitch=0.0&key=AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo"
    #savLoc = "/Users/mcah5a/Desktop/projects/slabStreetview-repo/streetviewInterface/mySite/media/"
    #fi = "1.jpg"
    #data = urllib.request.urlretrieve(url, os.path.join(savLoc,fi))




    return HttpResponse(url)




# Given GPS coordinates, return the heading value perpendicular to the road
def getHeading(request):
    context = {}
    return render(request, 'ImagePicker/panorama.html',context)


base = "https://maps.googleapis.com/maps/api/streetview?size=1200x800&location="
loc="457 West Robinwood Street, Detroit, Michigan 48203"
add="&key="
key="AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo"
url = base+loc+add+key
