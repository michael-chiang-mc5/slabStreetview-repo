import boto3
from mySite.settings import *
import sys

def main():
    # print command line arguments
    for arg in sys.argv[1:]:
        print(arg)
    print(AWS_ACCESS_KEY)
    print(AWS_SECRET)

if __name__ == "__main__":
    main()


