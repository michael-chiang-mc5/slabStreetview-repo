import boto3
from mySite.settings import *
import sys

# Example url:
# https://s3-us-west-1.amazonaws.com/slab-streetview/1.jpg

def main():
    # print command line arguments
    start_pk = int(sys.argv[1])
    end_pk = int(sys.argv[2])
    for pk in range(start_pk,end_pk+1):
        image_name = str(pk) + '.jpg'
        image_path = 'media/' + image_name
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET,)
        s3.upload_file(image_path, 'slab-streetview', image_name)
        print(image_path + ' uploaded to s3 as https://s3-us-west-1.amazonaws.com/slab-streetview/' + image_name)

if __name__ == "__main__":
    main()
