# Usage: python cloudvisreq.py API_KEY image1.jpg image2.png
# Code from: https://gist.github.com/dannguyen/a0b69c84ebc00c54c94d
# language codes: https://cloud.google.com/vision/docs/languages

from base64 import b64encode
from os import makedirs
from os.path import join, basename
from sys import argv
import json
import requests
from .models import *
from PIL import Image
import urllib.request, json, requests


ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
RESULTS_DIR = 'jsons'
makedirs(RESULTS_DIR, exist_ok=True)

def make_image_data_list(image_filenames):
    """
    image_filenames is a list of filename strings
    Returns a list of dicts formatted as the Vision API
        needs them to be
    """
    img_requests = []
    for imgname in image_filenames:
        with open(imgname, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            img_requests.append({
                    'image': {'content': ctxt},
                    'features': [{
                                    'type': 'TEXT_DETECTION',
                                    'maxResults': 1 }],
                    'imageContext': { 'languageHints': ["en","es",'zh','th','ko']} # language codes: https://cloud.google.com/vision/docs/languages
            })
    return img_requests

def make_image_data(image_filenames):
    """Returns the image data lists as bytes"""
    imgdict = make_image_data_list(image_filenames)
    return json.dumps({"requests": imgdict }).encode()


def request_ocr(api_key, image_filenames):
    response = requests.post(ENDPOINT_URL,
                             data=make_image_data(image_filenames),
                             params={'key': api_key},
                             headers={'Content-Type': 'application/json'})
    return response

def google_ocr_boundingBox(api_key, boundingBox):
    streetviewImage_url = join(settings.MEDIA_ROOT,boundingBox.streetviewImage.image.name)
    img = Image.open(streetviewImage_url)
    img = img.crop((boundingBox.x1_expanded(), boundingBox.y1_expanded(), boundingBox.x2_expanded(), boundingBox.y2_expanded() ))
    image_url = join(settings.MEDIA_ROOT,'temp_googleocr.jpg')
    img.save(image_url)

    image_filenames = [image_url]
    response = request_ocr(api_key, image_filenames)
    if response.status_code != 200 or response.json().get('error'):
        return(response.text)
    else:
        responses = response.json()['responses']
        for idx, resp in enumerate(responses): # response.json()['responses'][i] corresponds to ith image TODO: skip first image
            # Google OCR might not find any text
            if len(resp)==0:
                ocrText = OcrText(boundingBox=boundingBox,method='google',text='',notes='no text detected')
                ocrText.save()
                continue
            # save bounding box object
            t = resp['textAnnotations'][0]  # possible keys: fullTextAnnotation, textAnnotations
            locale = resp['textAnnotations'][0]['locale']
            annotation = resp['textAnnotations'][0]
            text = annotation['description']  # possible keys: description, boundingPoly, locale for FIRST element only
            ocrText = OcrText(boundingBox=boundingBox,method='google',text=text,locale='locale='+locale, notes=json.dumps(resp, indent=2))
            ocrText.save()

def google_ocr_api(api_key, streetviewImage):
    image_url = streetviewImage.image_url()
    print("running google ocr on " + image_url)
    #urllib.request.urlretrieve(image_url, 'deleteMe_google_ocr_api.jpg')
    try:
        request = urllib.request.urlopen(image_url,timeout=3)
    except:
        print("urlopen timeout")
        return
    with open('deleteMe_google_ocr_api.jpg','wb') as f:
        try:
            f.write(request.read())
        except:
            print("error writing image")
            return

    print("done retrieving image")
    image_filenames = ['deleteMe_google_ocr_api.jpg']
    response = request_ocr(api_key, image_filenames)

    if response.status_code != 200 or response.json().get('error'):
        print(response.text)
        raise ValueError('google ocr api failed')
    else:
        responses = response.json()['responses']
        googleocr = GoogleOCR(streetviewImage=streetviewImage,json_text=responses)
        googleocr.save()
        print("googleOCR generated")
    #pint("deleting file")
    #os.remove('deleteMe_google_ocr_api.jpg')
    #print("file deleted")

def google_ocr_streetviewImage(api_key, streetviewImage):
    image_url = join(settings.MEDIA_ROOT,streetviewImage.image.name)
    image_filenames = [image_url]
    response = request_ocr(api_key, image_filenames)
    if response.status_code != 200 or response.json().get('error'):
        return(response.text)
    else:
        responses = response.json()['responses']
        streetviewImage.notes = json.dumps(responses, indent=2)
        streetviewImage.save()
        for idx, resp in enumerate(responses): # response.json()['responses'][i] corresponds to ith image. Note we only run on one image
            # Google OCR might not find any text
            if len(resp)==0:
                boundingBox = BoundingBox(x1=0,x2=0,y1=0,y2=0,method='google',streetviewImage=streetviewImage)
                boundingBox.save() # it would be better to do the saving in the view, but we need to save to set OcrText.boundingBox
                ocrText = OcrText(boundingBox=boundingBox,method='google',text='',notes='empty')
                ocrText.save()
                continue
            # save bounding box object
            pages = resp['fullTextAnnotation']['pages']
            for page in pages:
                for block in page['blocks']:
                    for paragraph in block['paragraphs']:
                        vertices = paragraph['boundingBox']['vertices']
                        x1,x2,y1,y2 = sanitize_vertices(vertices)
                        locale = 'locale='+paragraph['property']['detectedLanguages'][0]['languageCode']
                        paragraph_text = ''
                        for word in paragraph['words']:
                            vertices = word['boundingBox']['vertices']
                            for symbol in word['symbols']:
                                paragraph_text = paragraph_text + symbol['text']
                                # refine vertices of bounding box
                                vertices = symbol['boundingBox']['vertices']
                                x1_tmp,x2_tmp,y1_tmp,y2_tmp = sanitize_vertices(vertices)
                                x1 = min(x1,x1_tmp)
                                x2 = max(x2,x2_tmp)
                                y1 = min(y1,y1_tmp)
                                y2 = max(y2,y2_tmp)
                            paragraph_text = paragraph_text + ' '
                        boundingBox = BoundingBox(x1=x1,x2=x2,y1=y1,y2=y2,method='google',streetviewImage=streetviewImage)
                        boundingBox.save() # it would be better to do the saving in the view, but we need to save to set OcrText.boundingBox
                        ocrText = OcrText(boundingBox=boundingBox,method='google',text=paragraph_text,locale=locale)
                        ocrText.save()

def sanitize_vertices(vertices):
    tmp = {}
    for idx in range(0,4):
        tmp.update({idx: {}})
        for dim in ['x','y']:
            try:
                val = vertices[idx][dim]
            except:
                val = 0
            tmp[idx].update({dim:val})
    x1 = min(tmp[0]['x'], tmp[1]['x'], tmp[2]['x'], tmp[3]['x'])
    x2 = max(tmp[0]['x'], tmp[1]['x'], tmp[2]['x'], tmp[3]['x'])
    y1 = min(tmp[0]['y'], tmp[1]['y'], tmp[2]['y'], tmp[3]['y'])
    y2 = max(tmp[0]['y'], tmp[1]['y'], tmp[2]['y'], tmp[3]['y'])
    return x1,x2,y1,y2




# This runs google OCR where individual words are segmented
def google_ocr_streetviewImage_byWord(api_key, streetviewImage):
    image_url = join(settings.MEDIA_ROOT,streetviewImage.image.name)
    image_filenames = [image_url]
    response = request_ocr(api_key, image_filenames)
    if response.status_code != 200 or response.json().get('error'):
        return(response.text)
    else:
        responses = response.json()['responses']
        streetviewImage.notes = json.dumps(responses, indent=2)
        streetviewImage.save()
        for idx, resp in enumerate(responses): # response.json()['responses'][i] corresponds to ith image. Note we only run on one image
            # Google OCR might not find any text
            if len(resp)==0:
                boundingBox = BoundingBox(x1=0,x2=0,y1=0,y2=0,method='google',streetviewImage=streetviewImage)
                boundingBox.save() # it would be better to do the saving in the view, but we need to save to set OcrText.boundingBox
                ocrText = OcrText(boundingBox=boundingBox,method='google',text='',notes='empty')
                ocrText.save()
                continue
            # save bounding box object
            pages = resp['fullTextAnnotation']['pages']
            for page in pages:
                for block in page['blocks']:
                    for paragraph in block['paragraphs']:
                        for word in paragraph['words']:
                            vertices = word['boundingBox']['vertices']
                            try:
                                x1 = min(vertices[0]['x'], vertices[1]['x'], vertices[2]['x'], vertices[3]['x']  )
                            except:
                                x1 = 0
                            try:
                                x2 = max(vertices[0]['x'], vertices[1]['x'], vertices[2]['x'], vertices[3]['x']  )
                            except:
                                x2 = 0
                            try:
                                y1 = min(vertices[0]['y'], vertices[1]['y'], vertices[2]['y'],  vertices[3]['y']  )
                            except:
                                y1 = 0
                            try:
                                y2 = max(vertices[0]['y'], vertices[1]['y'], vertices[2]['y'],  vertices[3]['y']  )
                            except:
                                y2 = 0
                            locale = 'locale='+word['property']['detectedLanguages'][0]['languageCode']
                            text = ''
                            for symbol in word['symbols']:
                                text = text + symbol['text']
                            boundingBox = BoundingBox(x1=x1,x2=x2,y1=y1,y2=y2,method='google',streetviewImage=streetviewImage)
                            boundingBox.save() # it would be better to do the saving in the view, but we need to save to set OcrText.boundingBox
                            ocrText = OcrText(boundingBox=boundingBox,method='google',text=text,locale=locale)
                            ocrText.save()


def google_ocr_streetviewImage_deprecated(api_key, streetviewImage):
    image_url = join(settings.MEDIA_ROOT,streetviewImage.image.name)
    image_filenames = [image_url]
    response = request_ocr(api_key, image_filenames)
    if response.status_code != 200 or response.json().get('error'):
        return(response.text)
    else:
        responses = response.json()['responses']
        for idx, resp in enumerate(responses): # response.json()['responses'][i] corresponds to ith image. Note we only run on one image
            # Google OCR might not find any text
            if len(resp)==0:
                boundingBox = BoundingBox(x1=0,x2=0,y1=0,y2=0,method='google',streetviewImage=streetviewImage)
                boundingBox.save() # it would be better to do the saving in the view, but we need to save to set OcrText.boundingBox
                ocrText = OcrText(boundingBox=boundingBox,method='google',text='',notes='')
                ocrText.save()
                streetviewImage.notes = "No google bounding boxes detected"
                streetviewImage.save()
                continue
            streetviewImage.notes = json.dumps(resp, indent=2)
            streetviewImage.save()
            # save bounding box object
            t = resp['textAnnotations'][0]  # possible keys: fullTextAnnotation, textAnnotations
            locale = resp['textAnnotations'][0]['locale']
            for i,annotation in enumerate(resp['textAnnotations']):
                if i==0: # skip first annotation. seems to be a composite
                    continue
                # bounding box
                text = annotation['description']  # possible keys: description, boundingPoly, locale for FIRST element only
                try:
                    x1 = min(annotation['boundingPoly']['vertices'][0]['x'], \
                             annotation['boundingPoly']['vertices'][1]['x'], \
                             annotation['boundingPoly']['vertices'][2]['x'], \
                             annotation['boundingPoly']['vertices'][3]['x']  )
                except:
                    x1 = 0
                try:
                    x2 = max(annotation['boundingPoly']['vertices'][0]['x'], \
                             annotation['boundingPoly']['vertices'][1]['x'], \
                             annotation['boundingPoly']['vertices'][2]['x'], \
                             annotation['boundingPoly']['vertices'][3]['x']  )
                except:
                    x2 = 0
                try:
                    y1 = min(annotation['boundingPoly']['vertices'][0]['y'], \
                             annotation['boundingPoly']['vertices'][1]['y'], \
                             annotation['boundingPoly']['vertices'][2]['y'], \
                             annotation['boundingPoly']['vertices'][3]['y']  )
                except:
                    y1 = 0
                try:
                    y2 = max(annotation['boundingPoly']['vertices'][0]['y'], \
                             annotation['boundingPoly']['vertices'][1]['y'], \
                             annotation['boundingPoly']['vertices'][2]['y'], \
                             annotation['boundingPoly']['vertices'][3]['y']  )
                except:
                    y2 = 0
                boundingBox = BoundingBox(x1=x1,x2=x2,y1=y1,y2=y2,method='google',streetviewImage=streetviewImage)
                boundingBox.save() # it would be better to do the saving in the view, but we need to save to set OcrText.boundingBox
                ocrText = OcrText(boundingBox=boundingBox,method='google',text=text,notes='locale='+locale)
                ocrText.save()
