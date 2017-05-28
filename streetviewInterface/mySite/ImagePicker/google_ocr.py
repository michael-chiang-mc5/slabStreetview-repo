# Usage: python cloudvisreq.py API_KEY image1.jpg image2.png
# Code from: https://gist.github.com/dannguyen/a0b69c84ebc00c54c94d

from base64 import b64encode
from os import makedirs
from os.path import join, basename
from sys import argv
import json
import requests
from .models import *


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
                        'maxResults': 1
                    }]
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
    streetviewImage_url = os.path.join(settings.MEDIA_ROOT,boundingBox.streetviewImage.image.name)
    img = Image.open(os.path.join(image_url))
    img = img.crop((boundingBox.x1, boundingBox.y1, boundingBox.x2, boundingBox.y2 ))
    image_url = os.path.join(settings.MEDIA_ROOT,'temp_googleocr.jpg')
    img.save(image_url)

    image_filenames = [image_url]
    response = request_ocr(api_key, image_filenames)
    if response.status_code != 200 or response.json().get('error'):
        return(response.text)
    else:
        responses = response.json()['responses']
        for idx, resp in enumerate(responses): # response.json()['responses'][i] corresponds to ith image TODO: skip first image
            # Google OCR might not find any text
            if len(resp)!=0:
                continue
            # save bounding box object
            t = resp['textAnnotations'][0]  # possible keys: fullTextAnnotation, textAnnotations
            locale = resp['textAnnotations'][0]['locale']
            for i,annotation in enumerate(resp['textAnnotations']):
                if i != 0:
                    continue
                # bounding box
                text = annotation['description']  # possible keys: description, boundingPoly, locale for FIRST element only
                x1 = min(annotation['boundingPoly']['vertices'][0]['x'], \
                         annotation['boundingPoly']['vertices'][1]['x'], \
                         annotation['boundingPoly']['vertices'][2]['x'], \
                         annotation['boundingPoly']['vertices'][3]['x']  )
                x2 = max(annotation['boundingPoly']['vertices'][0]['x'], \
                         annotation['boundingPoly']['vertices'][1]['x'], \
                         annotation['boundingPoly']['vertices'][2]['x'], \
                         annotation['boundingPoly']['vertices'][3]['x']  )
                y1 = min(annotation['boundingPoly']['vertices'][0]['y'], \
                         annotation['boundingPoly']['vertices'][1]['y'], \
                         annotation['boundingPoly']['vertices'][2]['y'], \
                         annotation['boundingPoly']['vertices'][3]['y']  )
                y2 = max(annotation['boundingPoly']['vertices'][0]['y'], \
                         annotation['boundingPoly']['vertices'][1]['y'], \
                         annotation['boundingPoly']['vertices'][2]['y'], \
                         annotation['boundingPoly']['vertices'][3]['y']  )
                ocrText = OcrText(boundingBox=boundingBox,method='google',text=text,notes='locale='+locale)
                ocrText.save()

def google_ocr_streetviewImage(api_key, streetviewImage):
    image_url = join(settings.MEDIA_ROOT,streetviewImage.image.name)
    image_filenames = [image_url]
    response = request_ocr(api_key, image_filenames)
    if response.status_code != 200 or response.json().get('error'):
        return(response.text)
    else:
        responses = response.json()['responses']
        for idx, resp in enumerate(responses): # response.json()['responses'][i] corresponds to ith image TODO: skip first image
            # Google OCR might not find any text
            if len(resp)==0:
                continue
            # save bounding box object
            t = resp['textAnnotations'][0]  # possible keys: fullTextAnnotation, textAnnotations
            locale = resp['textAnnotations'][0]['locale']
            for i,annotation in enumerate(resp['textAnnotations']): # skip first annotation? seems to be a composite
                if i==0:
                    continue
                # bounding box
                text = annotation['description']  # possible keys: description, boundingPoly, locale for FIRST element only
                x1 = min(annotation['boundingPoly']['vertices'][0]['x'], \
                         annotation['boundingPoly']['vertices'][1]['x'], \
                         annotation['boundingPoly']['vertices'][2]['x'], \
                         annotation['boundingPoly']['vertices'][3]['x']  )
                x2 = max(annotation['boundingPoly']['vertices'][0]['x'], \
                         annotation['boundingPoly']['vertices'][1]['x'], \
                         annotation['boundingPoly']['vertices'][2]['x'], \
                         annotation['boundingPoly']['vertices'][3]['x']  )
                y1 = min(annotation['boundingPoly']['vertices'][0]['y'], \
                         annotation['boundingPoly']['vertices'][1]['y'], \
                         annotation['boundingPoly']['vertices'][2]['y'], \
                         annotation['boundingPoly']['vertices'][3]['y']  )
                y2 = max(annotation['boundingPoly']['vertices'][0]['y'], \
                         annotation['boundingPoly']['vertices'][1]['y'], \
                         annotation['boundingPoly']['vertices'][2]['y'], \
                         annotation['boundingPoly']['vertices'][3]['y']  )
                boundingBox = BoundingBox(x1=x1,x2=x2,y1=y1,y2=y2,method='google',streetviewImage=streetviewImage)
                boundingBox.save() # it would be better to do the saving in the view, but we need to save to set OcrText.boundingBox
                ocrText = OcrText(boundingBox=boundingBox,method='google',text=text,notes='locale='+locale)
                ocrText.save()