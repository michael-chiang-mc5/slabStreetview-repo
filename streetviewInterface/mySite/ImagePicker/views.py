from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import os
import urllib.request
from django.conf import settings

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

    if request.method != 'POST':
        return HttpResponse("Must be POST")

    latitude = float(request.POST.get("latitude"))
    longitude = float(request.POST.get("longitude"))
    photographerHeading = float(request.POST.get("photographerHeading"))
    mapPoint = MapPoint(latitude=latitude, \
                        longitude=longitude, \
                        photographerHeading=photographerHeading)
    mapPoint.save()


    xdim = 640
    ydim = 400
    fov=140
    pitch=0

    saveImage(xdim,ydim,latitude,longitude,fov,photographerHeading+90,pitch,mapPoint)
    saveImage(xdim,ydim,latitude,longitude,fov,photographerHeading-90,pitch,mapPoint)

    return HttpResponse("done")

def saveImage(xdim,ydim,latitude,longitude,fov,heading,pitch,mapPoint):
    url =   "http://maps.googleapis.com/maps/api/streetview?size=%dx%d&location=%f,%f&fov=%d&heading=%f&pitch=%f&key=AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo" \
                 % (xdim,ydim,latitude,longitude,fov,heading,pitch)
    # left image
    streetviewImage = StreetviewImage(mapPoint=mapPoint, \
                                           heading=heading, \
                                           fov=fov, \
                                           pitch=pitch)
    streetviewImage.save()
    fi = str(streetviewImage.pk) + ".jpg"
    fi_path = os.path.join(settings.MEDIA_ROOT,fi)
    data = urllib.request.urlretrieve(url, fi_path)
    streetviewImage.image = fi # this should be set with respect to MEDIA_ROOT
    streetviewImage.save()




# Given GPS coordinates, return the heading value perpendicular to the road
def index(request):
    mapPoints = MapPoint.objects.all()
    context = {'mapPoints':mapPoints}
    return render(request, 'ImagePicker/panorama.html',context)
