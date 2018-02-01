import sys
import os
from .models import *



# Return true if line segments AB and CD intersect
# https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


# print out endpoint
def adsf(lng1,lat1,lng2,lat2):
    print(ParcelBoundarySegment.objects.count())
    return
    eps = 0.01
    pbss = ParcelBoundarySegment.objects.filter(endpoint1_lng__lt=eps+lng1 , \
                                         endpoint1_lng__gt=-eps+lng1, \
                                         endpoint1_lat__lt=eps+lat1 , \
                                         endpoint1_lat__gt=-eps+lat1, \
                                         endpoint2_lng__lt=eps+lng2 , \
                                         endpoint2_lng__gt=-eps+lng2, \
                                         endpoint2_lat__lt=eps+lat2 , \
                                         endpoint2_lat__gt=-eps+lat2, \
                                         )
    print(ParcelBoundarySegment.pbss.count())

    line_projection = ParcelBoundarySegment(endpoint1_lng=lng1, \
                                            endpoint1_lat=lat1, \
                                            endpoint2_lng=lng2, \
                                            endpoint2_lat=lat2, \
                                            )

    bf = [] # store distance and AIN
    for pbs in pbss:
        lines_intersect = intersect(pbs.A,pbs.B,line_projection.A,line_projection.B)
        if lines_intersect:
            # calculate distance
            pass





# Deletes all previous parcel boundary line segments
# Imports new parcel boundary line segments from csv to db
def import_parcel_boundary_to_db(csv_path=None):

    ParcelBoundarySegment.objects.all().delete()

    if csv_path is None:
        csv_path = 'media/PARCELS2015.csv'

    if not os.path.isfile(csv_path):
       print("File path {} does not exist. Exiting...".format(csv_path))
       sys.exit()

    with open(csv_path) as fp:
        next(fp) # skip csv header on first line
        cnt = 1
        for line in fp:
            print(cnt)
            # make sure multipolygon is formatted in a way we can reader
            if not 'MULTIPOLYGON (((' in line:
                print('{} not formatted correctly in {} (line {})'.format(line,csv_path,cnt))
                continue
            if not ')))"' in line:
                print('{} not formatted correctly in {} (line {})'.format(line,csv_path,cnt))
                continue

            multipolygon_str = line.split('",')[0] # extract multipolygon
            AIN = int(line.split('",')[1].split(',')[0])

            # get nested polygons
            bf = ''
            for ch in multipolygon_str:
                if ch is '(':
                    bf = ''
                    continue
                if ch is ')':
                    if len(bf) is 0:
                        continue
                    parse_bf_helper(bf,AIN)
                    bf = ''
                    continue
                bf += ch


            cnt += 1


def parse_bf_helper(bf,AIN):
    s = bf.split(',')
    for idx in range(len(s)-1):
        endpoint1 = s[idx]
        endpoint1_lng = float(endpoint1.split(' ')[-2])
        endpoint1_lat = float(endpoint1.split(' ')[-1])
        endpoint2 = s[idx+1]
        endpoint2_lng = float(endpoint2.split(' ')[-2])
        endpoint2_lat = float(endpoint2.split(' ')[-1])
        pbs = ParcelBoundarySegment(endpoint1_lng=endpoint1_lng, \
                              endpoint1_lat=endpoint1_lat, \
                              endpoint2_lng=endpoint2_lng, \
                              endpoint2_lat=endpoint2_lat, \
                              AIN=AIN, \
                              )
        pbs.save()

# Deletes all previous parcel boundary line segments
# Imports new parcel boundary line segments from csv to db
def import_parcel_boundary_to_db_deprecated(csv_path=None):

    ParcelBoundarySegment.objects.all().delete()

    if csv_path is None:
        csv_path = 'media/PARCELS2015.csv'

    if not os.path.isfile(csv_path):
       print("File path {} does not exist. Exiting...".format(csv_path))
       sys.exit()

    with open(csv_path) as fp:
        next(fp) # skip csv header on first line
        cnt = 1
        for line in fp:
            # make sure multipolygon is formatted in a way we can reader
            if not 'MULTIPOLYGON (((' in line:
                print('{} not formatted correctly in {} (line {})'.format(line,csv_path,cnt))
                continue
            if not ')))"' in line:
                print('{} not formatted correctly in {} (line {})'.format(line,csv_path,cnt))
                continue


            s1 = line.split('"')[1] # extract multipolygon string
            s2 = s1.split('(((')[1].split(')))')[0] # remove MULTIPOLYGON ((( )))
            s3 = s2.split(',') # Ex: ['-118.0 33.8', ' -118.068 33.8644', ' -118.0685745 33.8640721104']
            AIN = line.split('"')[2].split(',')[1]

            for idx in range(len(s3)-1):
                try:
                    endpoint1 = s3[idx]
                    endpoint1_lng = float(endpoint1.split(' ')[-2])
                    endpoint1_lat = float(endpoint1.split(' ')[-1])
                    endpoint2 = s3[idx+1]
                    endpoint2_lng = float(endpoint2.split(' ')[-2])
                    endpoint2_lat = float(endpoint2.split(' ')[-1])
                except:
                    print(endpoint1, endpoint2)
                    print(line)

                pbs = ParcelBoundarySegment(endpoint1_lng=endpoint1_lng, \
                                      endpoint1_lat=endpoint1_lat, \
                                      endpoint2_lng=endpoint2_lng, \
                                      endpoint2_lat=endpoint2_lat, \
                                      AIN=AIN, \
                                      )
                pbs.save()
            cnt += 1
