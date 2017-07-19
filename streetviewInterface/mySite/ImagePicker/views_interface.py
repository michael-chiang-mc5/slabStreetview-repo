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
from math import sqrt
from collections import Counter, defaultdict
from .google_ocr import *
import time
import sys
import subprocess
from random import randint
import json
import csv
from .views_saveImage import *
from .views_figures import *
from django.http import JsonResponse
from io import BytesIO

def metadata_zoning(request):
    mapPoint = MapPoint.objects.exclude(maptag__tag_type="zoning").first()
    if mapPoint is None:
        return HttpResponse("done")
    else:
        return JsonResponse({'pk':mapPoint.pk,'lon':mapPoint.longitude,'lat':mapPoint.latitude})

@csrf_exempt
def post_zoning(request):
    json_str = request.POST.get("json-str")
    d = json.loads(json_str)
    pk = int(d['pk']) # this is the pk of the mapPoint object
    zone = d['zone']
    mapTag = MapTag(mapPoint=MapPoint.objects.get(pk=pk),tag_type="zoning",tag_text=zone)
    mapTag.save()
    return HttpResponse('created tag for mapPoint.pk='+str(pk))

# POST data "json-str" should be python dictionary serialized to string
# should have fields: pk, box
# pk is the primary key of StreetviewImage object
# box should be (5,n)-matrix.
# box[i] gives ith bounding box
# box[i][j] gives x1,y1,x2,y2,nms for j=0,1,2,3,4
@csrf_exempt
def postBoundingBox(request):
    json_str = request.POST.get("json-str")
    d = ast.literal_eval(json_str)
    pk = d['pk'] # this is the pk of the Streetview object
    method = d['method']
    boxes = d['box']
    BoundingBox.objects.filter(streetviewImage=pk).delete() # delete previous bounding boxes
    if len(boxes)==0:
        boundingBox = BoundingBox(streetviewImage=StreetviewImage.objects.get(pk=pk),x1=-1, y1=-1, x2=-1, y2=-1,method=method, is_nil = True)
        boundingBox.save()
    for box in boxes:
        boundingBox = BoundingBox(streetviewImage=StreetviewImage.objects.get(pk=pk),x1=box[0], y1=box[1], x2=box[2], y2=box[3], score=box[4],method=method)
        boundingBox.save()
    return HttpResponse("done")

def list_CTPN_metadata(request):
    streetviewImage = StreetviewImage.valid_set().filter(image_is_set=True).exclude( boundingbox__method__contains="CTPN" ).first()
    if streetviewImage is None:
        return HttpResponse("done")
    else:
        streetviewImage.set_pending(True)
        return JsonResponse({'pk':streetviewImage.pk, 'url':streetviewImage.image_url()})

@csrf_exempt
def set_image_pending(request):
    json_str = request.POST.get("json-str")
    d = json.loads(json_str)
    #d = ast.literal_eval(json_str) # "true" is not the same as "True"
    pk = d['pk'] # this is the pk of the streetviewImage object
    pending = d['pending']
    if pending is True:
        StreetviewImage.objects.get(pk=pk).set_pending(True)
    if pending is False:
        StreetviewImage.objects.get(pk=pk).set_pending(False)
    return HttpResponse('set streetviewImage.pk='+str(pk)+' to pending='+str(pending))

@csrf_exempt
def postOCR(request):
    json_str = request.POST.get("json-str")
    d = ast.literal_eval(json_str)
    pk = d['pk'] # this is the pk of the boundingBox object
    method = d['method']
    text = d['text']
    notes = d['notes']
    locale = d['locale']
    score = d['score']
    OcrText.objects.filter(boundingBox=pk,method=method).delete() # delete previous results
    ocrText = OcrText(boundingBox=BoundingBox.objects.get(pk=pk),method=method,text=text,notes=notes,locale=locale,score=score)
    ocrText.save()
    return HttpResponse("done")


@csrf_exempt
def set_image_uploaded(request):
    json_str = request.POST.get("json-str")
    d = ast.literal_eval(json_str)
    pk = d['pk'] # this is the pk of the streetviewImage object
    streetviewImage=StreetviewImage.objects.get(pk=pk)
    streetviewImage.image_is_set = True
    streetviewImage.save()
    return HttpResponse('set streetviewImage.pk='+str(pk)+' to image_is_set=True')


def image_saver_metadata(request):
    streetviewImage = StreetviewImage.valid_set().filter(image_is_set=False).first()
    streetviewImage.set_pending(True)
    mapPoint = streetviewImage.mapPoint
    return JsonResponse({'xdim':640, 'ydim':640,'lat':mapPoint.latitude,'lon':mapPoint.longitude,\
                         'fov':streetviewImage.fov,'heading':streetviewImage.heading, 'pitch':streetviewImage.pitch,\
                         'name':streetviewImage.image_name(),'pk':streetviewImage.pk})




# metadata for CRNN
def list_crnn_metadata(request):
    boundingBoxes = BoundingBox.objects.exclude( ocrtext__method__contains="crnn" )
    response = HttpResponse(content_type='text/plain; charset=utf8')
    for boundingBox in boundingBoxes:
        response.write(str(boundingBox.pk)+"\t")
        #response.write("http://"+request.META['HTTP_HOST']+"/"+boundingBox.streetviewImage.image.url)
        response.write("http://"+request.META['HTTP_HOST']+reverse('ImagePicker:boundingBox', args=(boundingBox.pk,)))
        #response.write("\t"+str(boundingBox.x1)+"\t"+str(boundingBox.y1)+"\t"+str(boundingBox.x2)+"\t"+str(boundingBox.y2)+"\t"+str(boundingBox.nms))
        response.write("\n")
    return response

# metadata for ECN
def list_ECN_metadata(request):
    boundingBoxes = BoundingBox.objects.exclude( ocrtext__method__contains="ECN" )
    response = HttpResponse(content_type='text/plain; charset=utf8')
    for boundingBox in boundingBoxes:
        response.write(str(boundingBox.pk)+"\t")
        response.write("http://"+request.META['HTTP_HOST']+reverse('ImagePicker:boundingBox', args=(boundingBox.pk,)))
        response.write("\n")
    return response
