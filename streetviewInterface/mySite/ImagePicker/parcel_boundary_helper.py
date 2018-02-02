import sys
import os
from .models import *
from geopy.distance import vincenty
from django.db.models import Min, Max


# Return true if line segments AB and CD intersect
# https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

# print out endpoint
# lat1,lng1 = camera
# lat2,lng2 = projected line
def get_intersecting_AIN(lat1,lng1,lat2,lng2):
    eps = 0.01
    # filter only on 1 endpoint for speed
    pbs = ParcelBoundary.objects.filter(lng__lt=eps+lng1 , \
                                       lng__gt=-eps+lng1, \
                                       lat__lt=eps+lat1 , \
                                       lat__gt=-eps+lat1, \
                                       )

    max_d = 99999999999
    best_pb = None
    for pb in pbs: # iterate across parcel boundaries, which are composed of segments
        segments = pb.decode_segments()
        for idx in range(len(segments)-1): # iterate across line segments
            endpoint1 = segments[idx]
            endpoint2 = segments[idx+1]
            A = endpoint1
            B = endpoint2
            C = [lat1,lng1]
            D = [lat2,lng2]
            lines_intersect = intersect(A,B,C,D)
            if lines_intersect:
                # calculate intersection point
                px,py = calculate_intersection_point(lat1,lng1,lat2,lng2, \
                                                     endpoint1[0],endpoint1[1],endpoint2[0],endpoint2[1])
                #print('px,py=',px,py)
                # calculate distance from camera to intersection
                d = vincenty( (lat1,lng1), (px,py)).miles
                if d<max_d:
                    max_d = d
                    best_pb = pb

    if best_pb is None:
        return None
    else:
        print(best_pb.AIN)
        return best_pb.AIN

# print out endpoint
# lat1,lng1 = camera
def adsf_deprecated(lng1,lat1,lng2,lat2):
    print("starting...")
    #print(ParcelBoundarySegment.objects.count())

    eps = 0.01
    # filter only on 1 endpoint for speed
    pbss = ParcelBoundarySegment.objects.filter(endpoint1_lng__lt=eps+lng1 , \
                                         endpoint1_lng__gt=-eps+lng1, \
                                         endpoint1_lat__lt=eps+lat1 , \
                                         endpoint1_lat__gt=-eps+lat1, \
                                         )
    #print(pbss.count())
    print("done with filter")
    line_projection = ParcelBoundarySegment(endpoint1_lng=lng1, \
                                            endpoint1_lat=lat1, \
                                            endpoint2_lng=lng2, \
                                            endpoint2_lat=lat2, \
                                            )



    bf = [] # store distance and AIN
    max_d = 99999999999
    best_pbs = None
    for pbs in pbss:
        lines_intersect = intersect(pbs.A(),pbs.B(),line_projection.A(),line_projection.B())
        if lines_intersect:
            print(pbs.endpoint1_lat,',',pbs.endpoint1_lng)
            print(pbs.endpoint2_lat,',',pbs.endpoint2_lng)
            # calculate intersection point
            px,py = calculate_intersection_point(lat1,lng1,lat2,lng2, \
                                                 pbs.endpoint1_lat,pbs.endpoint1_lng,pbs.endpoint2_lat,pbs.endpoint2_lng)

            #print('px,py=',px,py)
            # calculate distance from camera to intersection
            d = vincenty( (lat1,lng1), (px,py)).miles
            if d<max_d:
                max_d = d
                best_pbs = pbs
    print("****")
    print(best_pbs.endpoint1_lat,',',best_pbs.endpoint1_lng)
    print(best_pbs.endpoint2_lat,',',best_pbs.endpoint2_lng)
    print(best_pbs.AIN)
    return best_pbs.AIN


def calculate_intersection_point(x1,y1,x2,y2,x3,y3,x4,y4):
    px =  ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / ( (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4) )
    py =  ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / ( (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4) )
    return px,py
# Deletes all previous parcel boundary line segments
# Imports new parcel boundary line segments from csv to db
def import_parcel_boundary_to_db(csv_path=None):
    print('starting import...')
    ParcelBoundary.objects.all().delete()
    print('done with delete')
    if csv_path is None:
        csv_path = 'media/PARCELS2015.csv'
    if not os.path.isfile(csv_path):
       print("File path {} does not exist. Exiting...".format(csv_path))
       sys.exit()

       # we will only read in parcels that fall within bounding box defined by MapPoints.
       min_lat = MapPoint.objects.filter().values_list('name').annotate(Min('latitude')).order_by('latitude')[0]
       min_lng = MapPoint.objects.filter().values_list('name').annotate(Min('longitude')).order_by('longitude')[0]
       max_lat = MapPoint.objects.filter().values_list('name').annotate(Min('latitude')).order_by('latitude')[0]
       max_lng = MapPoint.objects.filter().values_list('name').annotate(Min('longitude')).order_by('longitude')[0]
       bounding_box = [[min_lat,minlng],[max_lat,max_lng]]

       bounding_box = [[33.954406,-118.385114],[34.163178,-117.966947]]

    with open(csv_path) as fp:
        next(fp) # skip csv header on first line
        cnt = 1
        pbs_bf = []

        t = time.time()
        for line in fp:
            # make sure multipolygon is formatted in a way we can reader
            if not 'MULTIPOLYGON (((' in line:
                print('{} not formatted correctly in {} (line {})'.format(line,csv_path,cnt))
                continue
            if not ')))"' in line:
                print('{} not formatted correctly in {} (line {})'.format(line,csv_path,cnt))
                continue


            multipolygon_str = line.split('",')[0] # extract multipolygon
            try:
                AIN = int(line.split('",')[1].split(',')[0])
            except:
                print('{} not formatted correctly in {} (line {})'.format(line,csv_path,cnt))
                continue
            # get nested polygons
            bf = ''
            for ch in multipolygon_str:
                if ch is '(':
                    bf = ''
                    continue
                if ch is ')':
                    if len(bf) is 0:
                        continue
                    segments = parse_bf_helper(bf) # get list of pbs in str buffer
                    pb = ParcelBoundary(AIN=AIN)
                    pb.store_segments(segments)
                    #print(pb.decode_segments())
                    #print(pb)
                    pb.calculate_latlng()

                    # only store parcelBoundary if it falls within the bounding box
                    if pb.lat > bounding_box[0][0] and pb.lng > bounding_box[0][1] \
                    and pb.lat < bounding_box[1][0] and pb.lng < bounding_box[1][1]:
                        pbs_bf.append(pb) # concatenate
                    if len(pbs_bf) > 500:
                        print('writing to db, cnt' , cnt)
                        ParcelBoundary.objects.bulk_create(pbs_bf)
                        print(time.time() - t)
                        t=time.time()
                        #print(bf)
                        #print(ParcelBoundarySegment.objects.filter(AIN=AIN).count())
                        pbs_bf = []
                    bf = ''
                    continue
                bf += ch

            cnt += 1
        ParcelBoundary.objects.bulk_create(pbs_bf)
        print('cnt=',cnt)
        print(ParcelBoundary.objects.count())

# Deletes all previous parcel boundary line segments
# Imports new parcel boundary line segments from csv to db
def import_parcel_boundary_to_db_deprecated(csv_path=None):
    print('starting import...')
    ParcelBoundarySegment.objects.all().delete()
    if csv_path is None:
        csv_path = 'media/PARCELS2015.csv'
    if not os.path.isfile(csv_path):
       print("File path {} does not exist. Exiting...".format(csv_path))
       sys.exit()

    with open(csv_path) as fp:
        next(fp) # skip csv header on first line
        cnt = 1
        pbs_bf = []

        t = time.time()
        for line in fp:
            # make sure multipolygon is formatted in a way we can reader
            if not 'MULTIPOLYGON (((' in line:
                print('{} not formatted correctly in {} (line {})'.format(line,csv_path,cnt))
                continue
            if not ')))"' in line:
                print('{} not formatted correctly in {} (line {})'.format(line,csv_path,cnt))
                continue


            multipolygon_str = line.split('",')[0] # extract multipolygon
            try:
                AIN = int(line.split('",')[1].split(',')[0])
            except:
                continue
            # get nested polygons
            bf = ''
            for ch in multipolygon_str:
                if ch is '(':
                    bf = ''
                    continue
                if ch is ')':
                    if len(bf) is 0:
                        continue
                    pbs_list = parse_bf_helper(bf,AIN) # get list of pbs in str buffer
                    pbs_bf += pbs_list # concatenate
                    if len(pbs_bf) > 99999:
                        print('writing to db, cnt' , cnt)
                        ParcelBoundarySegment.objects.bulk_create(pbs_bf)
                        print(time.time() - t)
                        t=time.time()
                        #print(bf)
                        #print(ParcelBoundarySegment.objects.filter(AIN=AIN).count())
                        pbs_bf = []
                    bf = ''
                    continue
                bf += ch

            cnt += 1
        ParcelBoundarySegment.objects.bulk_create(pbs_bf)
        print('cnt=',cnt)
        print(ParcelBoundarySegment.objects.count())

def parse_bf_helper(bf):
    s = bf.split(',')
    rn = []
    for point_str in s:
        point_float = [ float(point_str.split(' ')[-1]),  float(point_str.split(' ')[-2])   ]   # [lat,lng]
        rn.append(point_float)
    return rn

def parse_bf_helper_deprecated(bf,AIN):
    s = bf.split(',')
    rn = []
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
        rn.append(pbs)
    return rn
