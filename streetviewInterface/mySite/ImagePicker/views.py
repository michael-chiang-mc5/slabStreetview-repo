from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import os
import urllib.request
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import ast
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

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

def listTextDetectorMetadata(request):
    streetviewImages_withoutBoundingBoxes = StreetviewImage.objects.filter(boundingbox__isnull=True)
    response = HttpResponse(content_type='text/plain; charset=utf8')
    for streetviewImage in streetviewImages_withoutBoundingBoxes:
        response.write(str(streetviewImage.pk) + "\t")
        response.write("http://")
        response.write(request.META['HTTP_HOST']+"/")
        response.write(streetviewImage.image.url)
        response.write("\n")
    return response

def listBoundingBox(request):
    boundingBoxes = BoundingBox.objects.all()
    response = HttpResponse(content_type='text/plain; charset=utf8')
    response.write("pk\timage_url\tx1\ty1\tx2\ty2\tnms\n")
    for boundingBox in boundingBoxes:
        response.write(str(boundingBox.streetviewImage.pk)+"\t")
        response.write("http://"+request.META['HTTP_HOST']+"/"+boundingBox.streetviewImage.image.url)
        response.write("\t"+str(boundingBox.x1)+"\t"+str(boundingBox.y1)+"\t"+str(boundingBox.x2)+"\t"+str(boundingBox.y2)+"\t"+str(boundingBox.nms))
        response.write("\n")
    return response

# POST data "json-str" should be python dictionary serialized to string
# should have fields: pk, box
# pk is the primary key of StreetviewImage object
# box should be (5,n)-matrix.
# box[i] gives ith bounding box
# box[i][j] gives x1,y1,x2,y2,nms for j=0,1,2,3,4
@csrf_exempt
def postBoundaryBox(request):
    json_str = request.POST.get("json-str")
    d = ast.literal_eval(json_str)
    pk = d['pk'] # this is the pk of the Streetview object
    boxes = d['box']
    BoundingBox.objects.filter(streetviewImage=pk).delete() # delete previous bounding boxes
    for box in boxes:
        boundingBox = BoundingBox(streetviewImage=StreetviewImage.objects.get(pk=pk),x1=box[0], y1=box[1], x2=box[2], y2=box[3], nms=box[4])
        boundingBox.save()
    return HttpResponse("done")

def deleteAllBoundingBox(request):
    BoundingBox.objects.all().delete()
    return HttpResponseRedirect(reverse('ImagePicker:adminPanel'))

def deleteAllStreetviewImages(request):
    StreetviewImage.objects.all().delete()
    return HttpResponseRedirect(reverse('ImagePicker:adminPanel'))

def deleteAllMapPoints(request):
    MapPoint.objects.all().delete()
    return HttpResponseRedirect(reverse('ImagePicker:adminPanel'))

def adminPanel(request):
    context = {}
    return render(request, 'ImagePicker/adminPanel.html',context)


# Given GPS coordinates, return the heading value perpendicular to the road
def index(request):
    mapPoints = MapPoint.objects.all()
    context = {'mapPoints':mapPoints}
    return render(request, 'ImagePicker/panorama.html',context)
