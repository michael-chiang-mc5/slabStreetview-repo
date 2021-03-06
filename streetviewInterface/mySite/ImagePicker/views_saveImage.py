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
from collections import Counter, defaultdict
from .google_ocr import *
import time
import sys
import subprocess
from random import randint
import json
import csv
import boto3
from random import randint
from time import sleep

def syncImages():
    streetviewImages = StreetviewImage.objects.all()
    for streetviewImage in streetviewImages:
        if streetviewImage.image_is_set is False:
            streetviewImage.check_if_image_is_set()
        else:
            print(str(streetviewImage.pk) + " was previously set")

def saveImages_async_deprecated():
    # parameters
    xdim = 640
    ydim = 640
    count_continuous_error = 0

    # get mapPoints
    mapPoints = MapPoint.objects.all()
    for mapPoint in mapPoints:

        # check if we should create the image
        # if we don't have exactly two streetviewImage objects, then we need to (re)create the images
        streetviewImages = mapPoint.streetviewimage_set.all()
        if len(streetviewImages) != 2:
            streetviewImages.delete()
            mapPoint.createStreetviewImages()
            recreate_image = True
        # if we have previously flagged streetviewImage objects as set, then we don't need to recreate
        elif streetviewImages[0].image_is_set and streetviewImages[1].image_is_set:
            recreate_image = False
            #print("skipping " + str(streetviewImages[0].pk) + " and " + str(streetviewImages[1].pk))
        # check if we need to recreate explicitly
        elif streetviewImages[0].check_if_image_is_set() and streetviewImages[1].check_if_image_is_set():
            streetviewImages[0].image_is_set = True
            streetviewImages[0].save()
            streetviewImages[1].image_is_set = True
            streetviewImages[1].save()
            recreate_image = False
            print("skipping " + str(streetviewImages[0].pk) + " and " + str(streetviewImages[1].pk))
        # we need to recreate image
        else:
            recreate_image = True

        try:
            if recreate_image:
                for streetviewImage in mapPoint.streetviewimage_set.all():
                    sleep(randint(0,6))
                    if settings.USE_S3:
                        image_name = 'temp6.jpg'
                        fi = saveConcatImage(xdim,ydim,mapPoint.latitude,mapPoint.longitude, \
                                             streetviewImage.fov,streetviewImage.heading,    \
                                             streetviewImage.pitch, image_name)
                        # upload image to s3
                        s3 = boto3.client('s3', \
                                            aws_access_key_id=settings.AWS_ACCESS_KEY,
                                            aws_secret_access_key=settings.AWS_SECRET, \
                                            )
                        s3.upload_file(fi, settings.AWS_BUCKET_NAME, streetviewImage.image_name())
                        streetviewImage.image_is_set = True
                        streetviewImage.save()
                        print(streetviewImage.image_name() + ' uploaded to s3')
                    else:
                        image_name = streetviewImage.image_name()
                        fi = saveConcatImage(xdim,ydim,mapPoint.latitude,mapPoint.longitude, \
                                             streetviewImage.fov,streetviewImage.heading,    \
                                             streetviewImage.pitch, image_name)
                        streetviewImage.image_is_set = True
                        streetviewImage.save()
                        print(streetviewImage.image_name() + ' saved')
                count_continuous_error = 0
        except BaseException as e:
            print(str(e))
            count_continuous_error += 1
            print("continuous error = " + str(count_continuous_error))
            if count_continuous_error > 3:
                break
            else:
                continue




# saves concatenated image from google streetview to local disk
def saveImages_async_deprecated():
    # get mapPoints
    mapPoints = MapPoint.objects.all()
    xdim = 640
    ydim = 640
    pitch=0
    for mapPoint in mapPoints:
        # check if image associated here to prevent worker collisions
        if mapPoint.streetviewimage_set.all().count() != 0:
            continue

        # fov right is wider because we are nearer to the right side of the road.
        for rl in [{'heading':mapPoint.photographerHeading+90,'fov':35}, \
                        {'heading':mapPoint.photographerHeading-90,'fov':22.5}]:
            # save object
            streetviewImage = StreetviewImage(mapPoint=mapPoint, \
                                                   heading=rl['heading'], \
                                                   fov=rl['fov'], \
                                                   pitch=pitch)
            streetviewImage.save()

            # make image, save local

            if settings.USE_S3:
                image_name = 'temp6.jpg'
                fi = saveConcatImage(xdim,ydim,mapPoint.latitude,mapPoint.longitude,rl['fov'],rl['heading'],pitch,image_name)
                # upload image to s3
                s3 = boto3.client('s3', \
                                    aws_access_key_id=settings.AWS_ACCESS_KEY,
                                    aws_secret_access_key=settings.AWS_SECRET, \
                                    )
                s3.upload_file(fi, settings.AWS_BUCKET_NAME, streetviewImage.image_name())
                print(streetviewImage.image_name() + ' uploaded to s3')
            else:
                image_name = streetviewImage.image_name()
                fi = saveConcatImage(xdim,ydim,mapPoint.latitude,mapPoint.longitude,rl['fov'],rl['heading'],pitch,image_name)
                print(streetviewImage.image_name() + ' saved')

def saveConcatImage(xdim,ydim,latitude,longitude,fov,heading,pitch,image_name):
    #saveImage2(xdim,ydim,latitude,longitude,fov,heading-(2*fov-0.5),pitch,'temp1.jpg')
    saveImage2(xdim,ydim,latitude,longitude,fov,heading-(fov-0.5),pitch,'temp2.jpg')
    saveImage2(xdim,ydim,latitude,longitude,fov,heading    ,pitch,'temp3.jpg')
    saveImage2(xdim,ydim,latitude,longitude,fov,heading+(fov-0.5),pitch,'temp4.jpg')
    #saveImage2(xdim,ydim,latitude,longitude,fov,heading+(2*fov-0.5),pitch,'temp5.jpg')

    #I1 = Image.open(os.path.join(settings.MEDIA_ROOT,'temp1.jpg'))
    I2 = Image.open(os.path.join(settings.MEDIA_ROOT,'temp2.jpg'))
    I3 = Image.open(os.path.join(settings.MEDIA_ROOT,'temp3.jpg'))
    I4 = Image.open(os.path.join(settings.MEDIA_ROOT,'temp4.jpg'))
    #I5 = Image.open(os.path.join(settings.MEDIA_ROOT,'temp5.jpg'))

    # crop
    #I1 = I1.crop((0, 0, I1.size[0], I1.size[1]-20))
    I2 = I2.crop((0, 0, I2.size[0], I2.size[1]-20))
    I3 = I3.crop((0, 0, I3.size[0], I3.size[1]-20))
    I4 = I4.crop((0, 0, I4.size[0], I4.size[1]-20))
    #I5 = I5.crop((0, 0, I5.size[0], I5.size[1]-20))


    I_concatenate = concatenateImage(I2,I3,'left')
    #I_concatenate = concatenateImage(I1,I_concatenate,'left')
    I_concatenate = concatenateImage(I_concatenate,I4,'right')
    #I_concatenate = concatenateImage(I_concatenate,I5,'right')

    # crop x-dimension ( 3600x620  to 2500x620    ) so that textDetector doesn't run out of memory
    #final_dimx = 2500
    #width, height = I_concatenate.size
    #I_concatenate = I_concatenate.crop((    round(width/2- final_dimx/2) , 0, round(width/2+ final_dimx/2), height))

    fi_path = os.path.join(settings.MEDIA_ROOT,image_name)
    I_concatenate.save(fi_path)
    #
    return fi_path

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

class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"

def saveImage2(xdim,ydim,latitude,longitude,fov,heading,pitch,filename):
    url =   "http://maps.googleapis.com/maps/api/streetview?size=%dx%d&location=%f,%f&fov=%d&heading=%f&pitch=%f"%(xdim,ydim,latitude,longitude,fov,heading,pitch) \
             + '&key='+ settings.GOOGLE_MAPS_API_KEY

    fi_path = os.path.join(settings.MEDIA_ROOT,filename)

    urllib._urlopener = AppURLopener()
    print(url)
    #urllib.URLopener.version = 'Mozilla/5.0' #  (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0
    data = urllib.request.urlretrieve(url, fi_path)
