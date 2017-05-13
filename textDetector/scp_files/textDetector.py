from urllib.request import urlopen
import urllib
from cfg import Config as cfg
# import cv2 # TODO
import requests, json

interface_url = "http://127.0.0.1:8000/" # TODO
metadata = interface_url + "ImagePicker/listTextDetectorMetadata/"
# http://127.0.0.1:8000/media/108.jpg

data = urlopen(metadata)
for line in data: # files are iterable
    line = line.decode("utf-8").split('\t')
    pk=line[0]
    pk=6
    image_url = line[1]
    image_save_path = "/Users/michaelchiang/Desktop/deleteMe.jpg" # must be absolute path TODO
    urllib.request.urlretrieve(image_url, image_save_path)

    # im=cv2.imread(image_save_path) TODO


    text_lines = [[  7.04000000e+02,   2.49455704e+02,   8.31000000e+02,   2.71221710e+02, 9.67289448e-01],
                  [  8.64000000e+02,   2.38295822e+02,   9.59000000e+02,   2.57278473e+02, 9.65643227e-01],
                  [  6.88000000e+02,   2.81915283e+02,   8.15000000e+02,   3.01560150e+02, 9.47555065e-01],
                  [  0.00000000e+00,   5.66411377e+02,   9.50000000e+01,   5.97335449e+02, 9.40665245e-01],
                  [  2.08000000e+02,   2.51678329e+02,   3.03000000e+02,   2.69474945e+02, 8.99835110e-01],
                  [  8.32000000e+02,   5.78626831e+02,   9.59000000e+02,   5.96769287e+02, 8.62056017e-01]]

    # get resize scaling factor
    #scale = cfg.SCALE
    #max_scale = cfg.MAX_SCALE
    #f=float(scale)/min(im.shape[0], im.shape[1])
    #if max_scale!=None and f*max(im.shape[0], im.shape[1])>max_scale:
    #    f=float(max_scale)/max(im.shape[0], im.shape[1])
    f=1.5 # TODO

    for i in range(len(text_lines)):
        text_line = text_lines[i]
        for j in range(len(text_line)-1):
            text_line[j] = round(text_line[j]/f)

    payload = {'pk':pk, 'box':text_lines}
    print(payload)

    post_url = interface_url + "ImagePicker/postBoundaryBox/"
    #r = requests.post(post_url, data=json.dumps(payload))
    r = requests.post(post_url, data={'json-str':json.dumps(payload)})

    text_file = open("/Users/michaelchiang/Desktop/deleteMe.html", "w")
    text_file.write(r.text)
    text_file.close()


    for line in text_lines:

        x1 = round(line[0]/f)
        y1 = round(line[1]/f)
        x2 = round(line[2]/f)
        y2 = round(line[3]/f)
        nms_score = line[4]

        #post_url = interface_url + "ImagePicker/postBoundaryBox/"
        #r = requests.post(interface_url+"", data=json.dumps(payload))
        #print(r.text)

        break
    break
