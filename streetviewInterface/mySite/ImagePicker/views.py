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
from .views_interface import *
from django.http import JsonResponse
from io import BytesIO
from django.db.models import Count



def deletePending(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    Pending.objects.all().delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])



def saveImages(request):
    #p = subprocess.Popen(['python', 'manage.py', 'saveImages'],
    #                                    stdout=subprocess.PIPE,
    #                                    stderr=subprocess.STDOUT)
    #context = {'message':"Save Images running. DO NOT RE-RUN!!"}
    #return render(request, 'ImagePicker/adminPanel.html',context)
    return HttpResponse("deprecated")

def boundingBox(request,boundingBox_pk):
    boundingBox = BoundingBox.objects.get(pk=boundingBox_pk)
    if boundingBox.is_nil == True:
        return HttpResponse("nil bounding box")
    image_url = boundingBox.streetviewImage.image_url()
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img = img.crop((boundingBox.x1, boundingBox.y1, boundingBox.x2, boundingBox.y2 ))
    response = HttpResponse(content_type="image/jpeg")
    img.save(response, "JPEG")
    return response

def boundingBox_expanded(request,boundingBox_pk):
    boundingBox = BoundingBox.objects.get(pk=boundingBox_pk)
    image_url = os.path.join(settings.MEDIA_ROOT,boundingBox.streetviewImage.image.name)
    img = Image.open(os.path.join(image_url))
    img = img.crop((boundingBox.x1_expanded(), boundingBox.y1_expanded(), boundingBox.x2_expanded(), boundingBox.y2_expanded() ))
    response = HttpResponse(content_type="image/jpeg")
    img.save(response, "JPEG")
    return response

def listImage(request):
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
    if request.method != 'POST':
        return HttpResponse("Must be POST")

    latitude = float(request.POST.get("latitude"))
    longitude = float(request.POST.get("longitude"))
    panoID = str(request.POST.get("panoID"))
    mapPointTag_str = str(request.POST.get("mapPointTag"))
    photographerHeading = float(request.POST.get("photographerHeading"))
    mapPoint = MapPoint(latitude=latitude, \
                        longitude=longitude, \
                        panoID=panoID, \
                        photographerHeading=photographerHeading, \
                        tag = mapPointTag_str)
    mapPoint.save()
    time.sleep(0.5)
    return HttpResponse("done")

# See: https://www.fcc.gov/general/census-block-conversions-api
def get_census_tracts():
    mapPoints = MapPoint.objects.filter(censusblock__isnull=True)
    url_template = 'http://data.fcc.gov/api/block/%d/find?format=json&latitude=%f&longitude=%f&showall=true'
    for mapPoint in mapPoints:
        url = url_template % (2010,mapPoint.latitude,mapPoint.longitude)
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
        # figure out whether intersection or single tract
        if 'intersection' in data['Block'].keys(): # if true, then we have intersection
            for el in data['Block']['intersection']:
                fips = el['FIPS']
                censusBlock = CensusBlock(mapPoint = mapPoint, fips = fips)
                censusBlock.save()
                print(censusBlock)
        else:
            fips = data['Block']['FIPS']
            censusBlock = CensusBlock(mapPoint = mapPoint, fips = fips)
            censusBlock.save()
            print(censusBlock)

def write_mapPoint():
    with open('output/MapPoints.csv', 'w') as csvfile:
        fieldnames = ['pk', 'latitude', 'longitude', 'num_boundingboxes','size_boundingboxes','zone_code','census_tracts']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        #mapPoints = MapPoint.objects.filter(streetviewimage__image_is_set=True).distinct()

        # get mapPoints where:
        #    mapPoint is associated with exactly two streetview images whose images are set
        #    mapPoint is associated with at least 1 CTPN boundingBoxes object (nil is ok)
        mapPoints = MapPoint.objects.extra(  select={'image_count':       'SELECT COUNT(*) FROM imagepicker_streetviewimage WHERE imagepicker_streetviewimage.mappoint_id = imagepicker_mappoint.id AND imagepicker_streetviewimage.image_is_set = 1',},
                                             where=['image_count = 2']
                                    ).filter(streetviewimage__boundingbox__method="CTPN").filter(censusblock__isnull=False).distinct()


        for mapPoint in mapPoints:
            writer.writerow({'pk':                  mapPoint.pk, \
                             'latitude':            mapPoint.latitude, \
                             'longitude':           mapPoint.longitude, \
                             'num_boundingboxes':   mapPoint.get_num_CTPN_boundingBoxes(), \
                             'size_boundingboxes':  mapPoint.get_size_CTPN_boundingBoxes(), \
                             'zone_code':           mapPoint.get_zone_code(), \
                             'census_tracts':       mapPoint.get_census_tracts(), \
                             #'photographerHeading': mapPoint.photographerHeading, \
                             #'panoID':              mapPoint.panoID, \
                             #'tag':                 mapPoint.tag, \
                             #'num_links':           mapPoint.num_links, \
                             #'address':             mapPoint.address, \
                             #'neighbors_panoID':      list(mapPoint.neighbors.all().values_list('panoID')) , \
                            })

def read_mapPoint(request):
    with open('output/MapPoints.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            pk                   = int(row[0])
            latitude             = float(row[1])
            longitude            = float(row[2])
            photographerHeading  = float(row[3])
            panoID               = str(row[4])
            tag                  = str(row[5])
            mapPoint = MapPoint(latitude=latitude, \
                                longitude=longitude, \
                                photographerHeading=photographerHeading, \
                                panoID=panoID, \
                                tag=tag, \
                                )
            mapPoint.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def listBoundingBox(request): # TODO: make urls to cropped image
    if request.method == 'POST':
        if not request.user.is_superuser:
            return HttpResponse("you are not an admin")
        cmd = request.POST.get("command")
        boundingBoxes = eval(cmd)
    else:
        boundingBoxes = BoundingBox.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(boundingBoxes, 10)
    try:
        boundingBoxes_page = paginator.page(page)
    except PageNotAnInteger:
        boundingBoxes_page = paginator.page(1)
    except EmptyPage:
        boundingBoxes_page = paginator.page(paginator.num_pages)

    context = {'boundingBoxes':boundingBoxes_page,'total_number':len(boundingBoxes),'num_images':len(StreetviewImage.objects.filter(boundingbox__in=boundingBoxes).distinct())}

    return render(request, 'ImagePicker/listBoundingBox.html',context)




def deleteAllOcr(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    OcrText.objects.all().delete()
    return HttpResponseRedirect(reverse('ImagePicker:adminPanel'))

def deleteAllBoundingBox(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    BoundingBox.objects.all().delete()
    return HttpResponseRedirect(reverse('ImagePicker:adminPanel'))

def deleteAllStreetviewImages(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    StreetviewImage.objects.all().delete()
    return HttpResponseRedirect(reverse('ImagePicker:adminPanel'))

def deleteStreetviewImage(request,streetviewImage_pk):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    streetviewImage = StreetviewImage.objects.get(pk=streetviewImage_pk)
    streetviewImage.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def deleteBoundingBox(request,pk):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    boundingBox = BoundingBox.objects.get(pk=pk)
    boundingBox.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def deleteAllMapPoints(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    MapPoint.objects.all().delete()
    return HttpResponseRedirect(reverse('ImagePicker:adminPanel'))

def adminPanel(request):
    context = {}
    return render(request, 'ImagePicker/adminPanel.html',context)

def benchmarkingPanel(request):
    num_benchmarked = len(BoundingBox.objects.filter( ocrtext__method__contains = "manual"))
    total = len(BoundingBox.objects.all())

    columns =   ['english','spanish','chinese','japanese'          ,'korean'   ,'thai'    ,'other']
    locations = ['woodman','pico'   ,'garvey' ,'tokyo(NONEXISTANT)','koreatown','thaitown','other(NONEXISTANT)']

    boundingBoxes = BoundingBox.objects.filter(method="google") # switch this to .all() when you want to benchmark over entire dataset, not just google ocr
    boundingBoxes_withManual = boundingBoxes.filter(ocrtext__method__contains="manual")

    # initialize confusion matrix
    confusion_matrix = {}
    for column_manual in columns:
        tmp = {}
        for column_ocr in columns:
            tmp.update({column_ocr:0})
        confusion_matrix.update({column_manual:tmp})
    # populate confusion matrix
    for boundingBox in boundingBoxes_withManual:
        benchmark = boundingBox.benchmark()
        if benchmark['language_manual'] is not None and benchmark['language_ocr'] is not None:
            language_manual = benchmark['language_manual']
            language_ocr = benchmark['language_ocr']
            confusion_matrix[language_manual][language_ocr] += 1
    # this is not a great name.
    # This is a matrix that tells how many signs of a certain language are in a given city
    benchmark_manual = {}
    for location in locations:
        tmp = {}
        for language in columns:
            tmp.update({language:0})
        benchmark_manual.update({location:tmp})
    # populate final result
    for boundingBox in boundingBoxes_withManual:
        benchmark = boundingBox.benchmark()
        if benchmark['language_manual'] is not None and benchmark['location'] is not None:
            location = benchmark['location']
            language = benchmark['language_manual']
            benchmark_manual[location][language] += 1

    #
    benchmark_ocr = {}
    for location in locations:
        tmp = {}
        for language in columns:
            tmp.update({language:0})
        benchmark_ocr.update({location:tmp})
    # populate final result
    for boundingBox in boundingBoxes_withManual:
        benchmark = boundingBox.benchmark()
        if benchmark['language_ocr'] is not None and benchmark['location'] is not None:
            location = benchmark['location']
            language = benchmark['language_ocr']
            benchmark_ocr[location][language] += 1

    context = {'num_benchmarked':num_benchmarked, 'total':total, \
              'confusion_matrix':confusion_matrix, 'benchmark_manual':benchmark_manual, \
              'benchmark_ocr':benchmark_ocr, 'columns':columns,'locations':locations}
    return render(request, 'ImagePicker/benchmarkingPanel.html',context)

def annotateRandomBoundingBox(request):
    boundingBoxes = BoundingBox.objects.exclude( ocrtext__method__contains = "manual")
    if boundingBoxes.count() - 1 < 0:
        return HttpResponse("no bounding boxes")
    idx = randint(0, boundingBoxes.count() - 1)
    boundingBox = boundingBoxes[idx]
    context = {'boundingBox':boundingBox}
    return render(request, 'ImagePicker/annotateRandomBoundingBox.html',context)

def postManualOCR(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    pk = request.POST.get("pk")
    method = "manual"
    text = request.POST.get("text")
    locale = request.POST.get("locale")
    notes = request.POST.get("notes")
    OcrText.objects.filter(boundingBox=pk,method=method).delete() # delete previous results
    ocrText = OcrText(boundingBox=BoundingBox.objects.get(pk=pk),notes=notes,method=method,text=text,locale=locale)
    ocrText.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def deleteDuplicateMapPoints(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    # get values of duplicate panoID
    #mapPoints = MapPoint.objects.all()
    #list_str = mapPoints.values_list('panoID')
    #duplicate = [k for k,v in Counter(list_str).items() if v>1]

    # delete duplicates
    for panoID in MapPoint.objects.values_list('panoID', flat=True).distinct():
        MapPoint.objects.filter(pk__in=MapPoint.objects.filter(panoID=panoID).values_list('id', flat=True)[1:]).delete()
    context = {}
    return render(request, 'ImagePicker/adminPanel.html',context)

def runLanguageIdentifiction(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    p = subprocess.Popen(['python', 'manage.py', 'languageIdentification'],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def runLanguageIdentifiction_async():
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    ocrTexts = OcrText.objects.filter(method='google', ocrlanguage__isnull=True)
    for ocrText in ocrTexts:
        ocrLanguage = OcrLanguage.init(ocrText) # saving done in method
    return HttpResponse("done")

def deleteAllOcrLanguage(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    OcrLanguage.objects.all().delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def run_google_ocr():
    max_count = 3

    # get list of all census FIPS
    FIPS = [el.tract_code() for el in CensusBlock.objects.all()]
    FIPS = list(set(FIPS))


    for FIP in FIPS:
        print("iterating through census tract " + FIP)
        censusBlocks = CensusBlock.objects.filter(fips__startswith=FIP)
        mapPoints = MapPoint.objects.filter(id__in=censusBlocks.values('mapPoint_id'))
        mapPoints = mapPoints.exclude(streetviewimage__image_is_set=False)
        mapPoints = mapPoints.filter(streetviewimage__boundingbox__isnull=False)
        mapPoints = mapPoints.distinct()
        mapPoints = sorted(mapPoints, key=lambda x: x.get_num_CTPN_boundingBoxes(), reverse=True)
        print(str(len(mapPoints)) + " mapPoints")
        count = 0
        while(1):
            if count >= len(mapPoints):
                print("no more map points")
                break
            mapPoint = mapPoints[count]
            streetviewImages = StreetviewImage.objects.filter(mapPoint=mapPoint)

            # check to see if both streetview images have image set
            skip = False
            for streetviewImage in streetviewImages:
                if streetviewImage.image_is_set == False:
                    print("image is not set, skipping")
                    skip = True
                    break
            if skip == True:
                continue

            for streetviewImage in streetviewImages:
                print("working on streetviewImage " + str(streetviewImage.pk))
                print(str(streetviewImage.count_boundingBoxes()) + " bounding boxes found")
                googleOCR = GoogleOCR.objects.filter(streetviewImage=streetviewImage)
                if len(googleOCR) == 0:
                    print("running google ocr on streetviewImage " + str(streetviewImage.pk))
                    google_ocr_api(settings.GOOGLE_OCR_API_KEY, streetviewImage)
                else:
                    print("previous google ocr found for streetviewImage " + str(streetviewImage.pk) + ", doing nothing")
            count += 1
            if count >= max_count:
                break
        print("************")


def runGoogleOCR_images(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    # get images without bounding boxes generated by google
    streetviewImages = StreetviewImage.objects.exclude( boundingbox__method__contains="google" )
    for streetviewImage in streetviewImages:
        google_ocr_streetviewImage(settings.GOOGLE_OCR_API_KEY, streetviewImage)
    context = {}
    return render(request, 'ImagePicker/adminPanel.html',context)

def runGoogleOCR_image(request,pk):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    if len(StreetviewImage.objects.filter( boundingbox__method__contains="google", pk__in=[int(pk)] )) > 0:
        return HttpResponse('google bounding box already generated previously')
    streetviewImage = StreetviewImage.objects.get(pk=pk)
    google_ocr_streetviewImage(settings.GOOGLE_OCR_API_KEY, streetviewImage)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def runGoogleOCR_randomImage(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    streetviewImages = StreetviewImage.objects.exclude( boundingbox__method__contains="google" )
    streetviewImage = streetviewImages[randint(0, streetviewImages.count() - 1)]
    return runGoogleOCR_image(request,streetviewImage.pk)

def runGoogleOCR_boundingBoxes(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    # get bounding boxes without ocr text generated by google
    boundingBoxes = BoundingBox.objects.exclude( ocrtext__method__contains="google" )
    for boundingBox in boundingBoxes:
        google_ocr_boundingBox(settings.GOOGLE_OCR_API_KEY, boundingBox)
    context = {}
    return render(request, 'ImagePicker/adminPanel.html',context)

def runGoogleOCR_manualOCR(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    # get bounding boxes without ocr text generated by google
    boundingBoxes = BoundingBox.objects.exclude( ocrtext__method__contains="google" ).filter( ocrtext__method__contains = "manual")
    for boundingBox in boundingBoxes:
        google_ocr_boundingBox(settings.GOOGLE_OCR_API_KEY, boundingBox)
    context = {}
    return render(request, 'ImagePicker/benchmarkingPanel.html',context)

def runGoogleOCR_boundingBox(request,boundingBox_pk):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    boundingBox = BoundingBox.objects.get(pk=boundingBox_pk)
    google_ocr_boundingBox(settings.GOOGLE_OCR_API_KEY, boundingBox)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
def deleteOcrText(request,ocrtext_pk):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    ocrText = OcrText.objects.get(pk=ocrtext_pk)
    ocrText.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Given GPS coordinates, return the heading value perpendicular to the road
def index(request):
    mapPoints = MapPoint.objects.all().count()
    mapPoints_withTags = MapPoint.objects.filter(maptag__isnull=False).distinct().count()
    streetviewImages = StreetviewImage.objects.filter(image_is_set=True).count()
    pending = Pending.objects.all().count()
    boundingBoxes = BoundingBox.objects.count()
    streetviewImages_withBB = StreetviewImage.objects.filter(image_is_set=True, boundingbox__isnull=False).distinct().count()
    mapPoints_withTract = MapPoint.objects.filter(censusblock__isnull=False).distinct().count()
    googleOCR = GoogleOCR.objects.count()
    FIPS = len(list(set([el.tract_code() for el in CensusBlock.objects.all()])))

    #mapPoints_noImage = [mapPoint for mapPoint in mapPoints if mapPoint.images_set() is False]
    #panoIdList = MapPoint.objects.values_list('panoID', flat=True)
    #numDuplicate_mapPoints = len(panoIdList) - len(set(panoIdList))

    #streetviewImages = [streetviewImage for streetviewImage in StreetviewImage.objects.all() if streetviewImage.image_is_set is True]

    #streetviewImages_no_google_BB = StreetviewImage.objects.exclude( boundingbox__method__contains="google" )
    #streetviewImages_no_CTPN_BB = StreetviewImage.objects.exclude( boundingbox__method__contains="CTPN" )

    #boundingBoxes = BoundingBox.objects.all()
    #boundingBoxes_no_google_text = BoundingBox.objects.exclude( ocrtext__method__contains="google" )
    #boundingBoxes_no_crnn_text = BoundingBox.objects.exclude( ocrtext__method__contains="crnn" )

    context = {'mapPoints':mapPoints,'streetviewImages':streetviewImages,'pending':pending,'boundingBoxes':boundingBoxes, \
               'streetviewImages_withBB':streetviewImages_withBB,'mapPoints_withTags':mapPoints_withTags, 'mapPoints_withTract':mapPoints_withTract, \
               'googleOCR':googleOCR, 'FIPS':FIPS}
    return render(request, 'ImagePicker/index.html',context)

def picker(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    mapPoints = MapPoint.objects.all()
    context = {'mapPoints':mapPoints,'api_key':settings.GOOGLE_MAPS_API_KEY}
    return render(request, 'ImagePicker/panorama.html',context)

def routePicker(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    mapPoints = MapPoint.objects.all()
    context = {'mapPoints':mapPoints,'api_key':settings.GOOGLE_MAPS_API_KEY}
    return render(request, 'ImagePicker/route.html',context)

def crawler(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    mapPoints = MapPoint.objects.all()
    #context = {'api_key':settings.GOOGLE_MAPS_API_KEY,'mapPoints':MapPoint.objects.all()}
    context = {'api_key':settings.GOOGLE_MAPS_API_KEY}
    return render(request, 'ImagePicker/crawler.html',context)


def initialize_bfs(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    CrawlerQueueEntry.objects.all().delete()
    # TODO: set MapPoint.panoID = None for all pre-existing
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Takes POST data
# saves mapPoint
# downloads associated streetview images to point and saves streetviewImage (2 per mapPoint for right and left)
def bfs(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    # TODO: check whether distance from start point exceeds a given limit
    time.sleep(0.3)

    panoID = str(request.POST.get("panoID"))
    links = request.POST.getlist("links[]")

    # If we start from a point that is already in dataset (
    # this can happen when if we have two separatedly initialized blobs merging)
    # Suppose I initilize and run blob one.
    # Then, I initilize blob two on the periphery of blob one
    # Since I have not reset the queue for Blob one, a link in blob two could point to a point in blob one
    # This logic is complicated and only applies when the two blobs are running at the same time.
    # Therefore, I have disabled running two blobs at the same time (must delete queue before new blob)

    #    - we do not save point
    #    - should still delete point from queue
    #    - we should still save links to queue if links do not already exist in queue
    #    - we should still construct edge to neighbors (although I don't think this is necessary)
    match = MapPoint.objects.filter(panoID=panoID)
    if len(match) == 0:
        # save point
        latitude = float(request.POST.get("latitude"))
        longitude = float(request.POST.get("longitude"))
        mapPointTag_str = str(request.POST.get("mapPointTag"))
        photographerHeading = float(request.POST.get("photographerHeading"))
        address = str(request.POST.get("address"))
        mapPoint = MapPoint(latitude=latitude, \
                            longitude=longitude, \
                            panoID=panoID, \
                            photographerHeading=photographerHeading, \
                            tag=mapPointTag_str, \
                            num_links=len(links), \
                            address=str(address) \
                            )
        mapPoint.save()

        # also save streetview images while we are at it
        # this is so we can run image saving off-site
        mapPoint.createStreetviewImages()

        # save links to queue
        for link in links:
            match_link = MapPoint.objects.filter(panoID=link) # check if link is already saved as mapPoint
            if len(match_link)==0:
                cqe = CrawlerQueueEntry(panoID=link)
                cqe.save()
            elif len(match_link)==1:
                match_link[0].neighbors.add(mapPoint)
            else:
                return HttpResponse("error: duplicate map points found while linking. Please resolve this")

        # no warning
        warning = ''
    elif len(match) == 1:
        # collision. This should not happen as long as you delete queue before starting new run
        # i think javascript might be spawning multiple threads
        warning = "warning: collision at " + panoID + " probably due to thread collision"
    else:
        return HttpResponse("error: duplicate map points found. Please resolve this")


    # delete point from queue
    CrawlerQueueEntry.objects.filter(panoID=panoID).delete()
    # return panoID of next node to visit
    next_node = CrawlerQueueEntry.objects.order_by('time').first()
    if next_node is None:
        return HttpResponse('terminate')
    else:
        data = {}
        data['pano_id'] = next_node.panoID
        #data['queue']   = list(CrawlerQueueEntry.objects.values_list('panoID').order_by('time'))
        data['warning'] = warning
        return HttpResponse(json.dumps(data), content_type = "application/json")

def get_current_bfs_queue_item(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not an admin")
    next_node = CrawlerQueueEntry.objects.order_by('time').first()
    if next_node is None:
        return HttpResponse('terminate')
    else:
        return HttpResponse(next_node.panoID)
