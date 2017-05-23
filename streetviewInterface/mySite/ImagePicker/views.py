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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from PIL import Image
from math import sqrt

def boundingBox(request,boundingBox_pk):
    boundingBox = BoundingBox.objects.get(pk=boundingBox_pk)
    image_url = os.path.join(settings.MEDIA_ROOT,boundingBox.streetviewImage.image.name)
    img = Image.open(os.path.join(image_url))
    img = img.crop((boundingBox.x1, boundingBox.y1, boundingBox.x2, boundingBox.y2 ))
    response = HttpResponse(content_type="image/jpeg")
    img.save(response, "JPEG")
    return response

def listImage(request):
    #return savePoint(request)
    streetviewImages = StreetviewImage.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(streetviewImages, 10)
    try:
        streetviewImages_page = paginator.page(page)
    except PageNotAnInteger:
        streetviewImages_page = paginator.page(1)
    except EmptyPage:
        streetviewImages_page = paginator.page(paginator.num_pages)

    context = {'streetviewImages':streetviewImages_page}

    return render(request, 'ImagePicker/listImage.html',context)

# Takes POST data
# saves mapPoint
# downloads associated streetview images to point and saves streetviewImage (2 per mapPoint for right and left)
def savePoint(request):
    #url = "http://maps.googleapis.com/maps/api/streetview?size=640x640&location=42.34554965704973,-71.09832376428187&fov=90&heading=270.0&pitch=0.0&key=AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo"
    #url = "http://maps.googleapis.com/maps/api/streetview?size=640x640&location=34.14583813149605,-118.13731629652199&fov=90&heading=179.3621063232422&pitch=0.0&key=AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo"

    #savLoc = "/Users/mcah5a/Desktop/projects/slabStreetview-repo/streetviewInterface/mySite/media/"
    #fi = "1.jpg"
    #data = urllib.request.urlretrieve(url, os.path.join(savLoc,fi))

    if request.method != 'POST':
        return HttpResponse("Must be POST")

    latitude = float(request.POST.get("latitude"))
    longitude = float(request.POST.get("longitude"))
    panoID = str(request.POST.get("panoID"))
    photographerHeading = float(request.POST.get("photographerHeading"))
    mapPoint = MapPoint(latitude=latitude, \
                        longitude=longitude, \
                        panoID=panoID, \
                        photographerHeading=photographerHeading)
    mapPoint.save()


    xdim = 640
    ydim = 640
    fov_right=35
    fov_left=22.5
    pitch=0

    saveConcatImage(xdim,ydim,latitude,longitude,fov_right,photographerHeading+90,pitch,mapPoint)
    saveConcatImage(xdim,ydim,latitude,longitude,fov_left,photographerHeading-90,pitch,mapPoint)

    return HttpResponse("done")

def saveConcatImage(xdim,ydim,latitude,longitude,fov,heading,pitch,mapPoint):
    saveImage2(xdim,ydim,latitude,longitude,fov,heading-(2*fov-0.5),pitch,'temp1.jpg')
    saveImage2(xdim,ydim,latitude,longitude,fov,heading-(fov-0.5),pitch,'temp2.jpg')
    saveImage2(xdim,ydim,latitude,longitude,fov,heading    ,pitch,'temp3.jpg')
    saveImage2(xdim,ydim,latitude,longitude,fov,heading+(fov-0.5),pitch,'temp4.jpg')
    saveImage2(xdim,ydim,latitude,longitude,fov,heading+(2*fov-0.5),pitch,'temp5.jpg')

    I1 = Image.open(os.path.join(settings.MEDIA_ROOT,'temp1.jpg'))
    I2 = Image.open(os.path.join(settings.MEDIA_ROOT,'temp2.jpg'))
    I3 = Image.open(os.path.join(settings.MEDIA_ROOT,'temp3.jpg'))
    I4 = Image.open(os.path.join(settings.MEDIA_ROOT,'temp4.jpg'))
    I5 = Image.open(os.path.join(settings.MEDIA_ROOT,'temp5.jpg'))

    # crop
    I1 = I1.crop((0, 0, I1.size[0], I1.size[1]-20))
    I2 = I2.crop((0, 0, I2.size[0], I2.size[1]-20))
    I3 = I3.crop((0, 0, I3.size[0], I3.size[1]-20))
    I4 = I4.crop((0, 0, I4.size[0], I4.size[1]-20))
    I5 = I5.crop((0, 0, I5.size[0], I5.size[1]-20))


    I_concatenate = concatenateImage(I2,I3,'left')
    I_concatenate = concatenateImage(I1,I_concatenate,'left')
    I_concatenate = concatenateImage(I_concatenate,I4,'right')
    I_concatenate = concatenateImage(I_concatenate,I5,'right')

    # crop x-dimension ( 3600x620  to 2500x620    ) so that textDetector doesn't run out of memory
    final_dimx = 2500
    width, height = I_concatenate.size
    I_concatenate = I_concatenate.crop((    round(width/2- final_dimx/2) , 0, round(width/2+ final_dimx/2), height))

    # save StreetviewImage object
    streetviewImage = StreetviewImage(mapPoint=mapPoint, \
                                           heading=heading, \
                                           fov=fov, \
                                           pitch=pitch)
    streetviewImage.save()
    fi = str(streetviewImage.pk) + ".jpg"
    fi_path = os.path.join(settings.MEDIA_ROOT,fi)
    # save concatenated image
    I_concatenate.save(fi_path)
    #
    streetviewImage.image = fi # this should be set with respect to MEDIA_ROOT
    streetviewImage.save()


def concatenateImage(I_left, I_right, shiftRightOrLeft):
    # get column of right-most pixels for I_left and left-most pixels for I_right
    column_left  = get_column(I_left,'last')
    column_right = get_column(I_right,'first')
    # find shift that minimizes distance
    dimy = len(column_left)
    shift_range = int(dimy/6) # decrease to speed up
    min_average_distance = float("inf")
    shift = 0
    for i in range(-shift_range,shift_range):
        sum_distance = 0
        count = 0
        for j in range(0,dimy):
            if j+i<0 or j+i>=dimy:
                continue
            else:
                v1 = column_left[j]
                v2 = column_right[j+i]
                distance = sqrt(  (v1[0]-v2[0])**2 + (v1[1]-v2[1])**2 + (v1[2]-v2[2])**2  )
                sum_distance += distance
                count = count + 1
        average_distance = sum_distance/count
        if average_distance < min_average_distance:
            min_average_distance=average_distance
            shift=i
    # shift right image to match left image
    if shiftRightOrLeft == 'right':
        I_right_shift = Image.new('RGB', (I_right.size[0], I_right.size[1]))
        I_right_shift.paste(I_right, (0,-shift))
        # concatenate right and left image
        dimy = max(I_left.size[1],I_right_shift.size[1])
        dimx = I_left.size[0]+I_right_shift.size[0]
        I_concatenate = Image.new('RGB', (dimx,dimy))
        I_concatenate.paste(I_left, (0,0))
        I_concatenate.paste(I_right_shift, (I_left.size[0],0))
    elif shiftRightOrLeft == 'left':
        I_left_shift = Image.new('RGB', (I_left.size[0], I_left.size[1]))
        I_left_shift.paste(I_left, (0,shift))
        # concatenate right and left image
        dimy = max(I_right.size[1],I_left_shift.size[1])
        dimx = I_right.size[0]+I_left_shift.size[0]
        I_concatenate = Image.new('RGB', (dimx,dimy))
        I_concatenate.paste(I_left_shift, (0,0))
        I_concatenate.paste(I_right, (I_left_shift.size[0],0))
    return I_concatenate

def get_column(I,firstOrLast):
    pix = I.load()
    dimx = I.size[0]
    dimy = int(I.size[1])
    column = [None]*dimy
    for i in range(0,dimy):
        if firstOrLast == 'first':
            column[i] = pix[0,i]
        elif firstOrLast == 'last':
            column[i] = pix[dimx-1,i]
    return column

def saveImage2(xdim,ydim,latitude,longitude,fov,heading,pitch,filename):
    url =   "http://maps.googleapis.com/maps/api/streetview?size=%dx%d&location=%f,%f&fov=%d&heading=%f&pitch=%f&key=AIzaSyBrwkUADkwqTvlC-HbKC_jZuqC3xBxUNLo" \
                 % (xdim,ydim,latitude,longitude,fov,heading,pitch)
    fi_path = os.path.join(settings.MEDIA_ROOT,filename)
    data = urllib.request.urlretrieve(url, fi_path)

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

    page = request.GET.get('page', 1)
    paginator = Paginator(boundingBoxes, 100)
    try:
        boundingBoxes_page = paginator.page(page)
    except PageNotAnInteger:
        boundingBoxes_page = paginator.page(1)
    except EmptyPage:
        boundingBoxes_page = paginator.page(paginator.num_pages)

    context = {'boundingBoxes':boundingBoxes_page}

    return render(request, 'ImagePicker/listBoundingBox.html',context)

def listBoundingBoxMetadata(request):
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

def routePicker(request):
    mapPoints = MapPoint.objects.all()
    context = {'mapPoints':mapPoints}
    return render(request, 'ImagePicker/route.html',context)
