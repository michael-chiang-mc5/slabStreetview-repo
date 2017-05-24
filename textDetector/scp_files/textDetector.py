import urllib
import requests, json

from cfg import Config as cfg
from other import draw_boxes, resize_im, CaffeModel
import cv2, os, caffe, sys
from detectors import TextProposalDetector, TextDetector
import os.path as osp
from utils.timer import Timer

NET_DEF_FILE="models/deploy.prototxt"
MODEL_FILE="models/ctpn_trained_model.caffemodel"
scaling_method = 2


caffe.set_mode_gpu()
caffe.set_device(cfg.TEST_GPU_ID)

# initialize the detectors
text_proposals_detector=TextProposalDetector(CaffeModel(NET_DEF_FILE, MODEL_FILE))
text_detector=TextDetector(text_proposals_detector)

interface_url = "http://104.131.145.75/"
metadata = interface_url + "ImagePicker/listTextDetectorMetadata/"
data = urllib.urlopen(metadata)
#data = ['81\thttp://104.131.145.75/media/81.jpg']

for line in data: # each line is pk, image_url
    line = line.decode("utf-8").split('\t')
    pk=line[0]
    image_url = line[1]
    image_save_path = "/home/ubuntu/CTPN/tools/deleteMe.jpg" # must be absolute path TODO
    urllib.urlretrieve(image_url, image_save_path)

    # run text detection
    im=cv2.imread(image_save_path)
    dimy = im.shape[0]
    dimx = im.shape[1]

    if scaling_method == 1:
        im, f=resize_im(im, cfg.SCALE, cfg.MAX_SCALE)
    elif scaling_method == 2:
        f=1.2
        im=cv2.resize(im, (0, 0), fx=f, fy=f)

    text_lines=text_detector.detect(im)

    # apply scaling factor
    for i in range(len(text_lines)):
        text_line = text_lines[i]
        for j in range(len(text_line)-1):
            text_line[j] = round(text_line[j]/f)

    # post to interface
    payload = {'pk':pk, 'box':text_lines.tolist()}
    post_url = interface_url + "ImagePicker/postBoundingBox/"
    r = requests.post(post_url, data={'json-str':json.dumps(payload)})
    #text_file = open("/Users/michaelchiang/Desktop/deleteMe.html", "w")
    #text_file.write(r.text)
    #text_file.close()
