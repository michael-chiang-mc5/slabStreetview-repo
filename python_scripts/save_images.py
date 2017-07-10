import secret_keys
import boto3
import urllib.request, json, requests
from PIL import Image
import os
from math import sqrt

# Example url:
# https://s3-us-west-1.amazonaws.com/slab-streetview/1.jpg


#interface_url = "http://127.0.0.1:8000/"
#AWS_BUCKET_NAME = 'slab-streetview-debug'
interface_url = "http://104.131.145.75/"
AWS_BUCKET_NAME = 'slab-streetview'

def main():
    count_continuous_error = 0
    r = requests.get('https://api.ipify.org/')
    if r.text = '172.249.49.159':
        GOOGLE_KEY = GOOGLE_KEY_BRIDGEPORT
    else:
        print("No key")
        return

    while(1):
        # get metadata
        with urllib.request.urlopen(interface_url+"ImagePicker/image_saver_metadata/") as url: # TODO: update to 104....
            data = json.loads(url.read().decode())
            try:
                create_and_upload_image(data)
            except BaseException as e:
                print("ERROR : " + str(e))
                if str(e) == 'HTTP Error 500: Internal Server Error': # google
                    pass
                count_continuous_error += 1
                print("continuous error = " + str(count_continuous_error))
                if count_continuous_error > 4:
                    break
                else:
                    continue

def create_and_upload_image(data):
    print('attempting to save '+data['name'] + ' to local')
    # tell server to set pending so we don't assign twice
    payload = {'pk':data['pk'],'pending':True}
    post_url = interface_url + "ImagePicker/set_image_pending/"
    r = requests.post(post_url, data={'json-str':json.dumps(payload)})
    #text_file = open("debug.html", "w")
    #text_file.write(r.text)
    #text_file.close()
    # create and save image locally
    fi = saveConcatImage(data['xdim'],data['ydim'],data['lat'],data['lon'], \
                         data['fov'],data['heading'],    \
                         data['pitch'], data['name'])
    # upload image to s3
    s3 = boto3.client('s3',aws_access_key_id=secret_keys.AWS_ACCESS_KEY,aws_secret_access_key=secret_keys.AWS_SECRET)
    s3.upload_file(fi, AWS_BUCKET_NAME, data['name'])
    print(data['name'] + ' uploaded to s3')
    # tell server to set image is uploaded
    payload = {'pk':data['pk']}
    post_url = interface_url + "ImagePicker/set_image_uploaded/"
    r = requests.post(post_url, data={'json-str':json.dumps(payload)})
    # tell server to unset pending
    payload = {'pk':data['pk'],'pending':False}
    post_url = interface_url + "ImagePicker/set_image_pending/"
    r = requests.post(post_url, data={'json-str':json.dumps(payload)})

def saveConcatImage(xdim,ydim,latitude,longitude,fov,heading,pitch,image_name):
    # save to local
    saveImage2(xdim,ydim,latitude,longitude,fov,heading-(fov-0.5),pitch,'temp2.jpg')
    saveImage2(xdim,ydim,latitude,longitude,fov,heading    ,pitch,'temp3.jpg')
    saveImage2(xdim,ydim,latitude,longitude,fov,heading+(fov-0.5),pitch,'temp4.jpg')
    # open
    I2 = Image.open('temp2.jpg')
    I3 = Image.open('temp3.jpg')
    I4 = Image.open('temp4.jpg')
    # crop
    I2 = I2.crop((0, 0, I2.size[0], I2.size[1]-20))
    I3 = I3.crop((0, 0, I3.size[0], I3.size[1]-20))
    I4 = I4.crop((0, 0, I4.size[0], I4.size[1]-20))
    # concatenate
    I_concatenate = concatenateImage(I2,I3,'left')
    I_concatenate = concatenateImage(I_concatenate,I4,'right')
    # save concatenated imae
    I_concatenate.save('temp.jpg')
    return 'temp.jpg'


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
    version = "Mozilla/5.0" # 'Mozilla/5.0' (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0

def saveImage2(xdim,ydim,latitude,longitude,fov,heading,pitch,filename):
    url =   "http://maps.googleapis.com/maps/api/streetview?size=%dx%d&location=%f,%f&fov=%d&heading=%f&pitch=%f"%(xdim,ydim,latitude,longitude,fov,heading,pitch) \
             + '&key='+ secret_keys.GOOGLE_KEY
    urllib._urlopener = AppURLopener()
    print('saving image from '+url)
    data = urllib.request.urlretrieve(url, filename)

if __name__ == "__main__":
    main()
