# the_geom,SHAPE_LEN,SHAPE_AREA,ZONE_CMPLT
# geometry,

import re
import numpy as np
import scipy.spatial
import time
import pickle
import os.path
import urllib.request, json, requests

def parse_geometry(the_geom_str):
    the_geom_str = re.sub("[^0-9,. -]", "", the_geom_str)
    tmp = the_geom_str.split(',')
    lonlat = len(tmp)*[None]
    for i,el in enumerate(tmp):
        coordinates = el.split(' ')
        lonlat[i] = [float(coordinates[1]),float(coordinates[2])]
    return lonlat

def parse_zoning(zoning_str):
    # remove (*),[*]
    zoning_str = re.sub("\[[a-zA-Z]\]|\([a-zA-Z]\)", "", zoning_str)
    tmp = zoning_str.split('-')
    if len(tmp) == 1:
        code = tmp[0][:-1]
    else:
        code = zoning_str.split('-')[0]
    if code[0] == 'T' or code[0] == 'Q' or code[0] == 'D':
        code = code[1:]
    return code

def compute_center(lonlat_arr):
    sum_lon = 0
    sum_lat = 0
    for lonlat in lonlat_arr:
        sum_lon += lonlat[0]
        sum_lat += lonlat[1]
    return sum_lon/len(lonlat_arr), sum_lat/len(lonlat_arr)


def parse_line(line):
    tmp = line.split(',')
    zoning = parse_zoning(tmp[-1])
    area   = tmp[-2]
    length = tmp[-3]
    the_geom_str = ','.join(tmp[:-3])

    # get array of longitude/latitude pairs
    lonlat = parse_geometry(the_geom_str)
    lon,lat = compute_center(lonlat)

    return zoning,area,length,[lon,lat]


# see sum_of_zone.pdf
# A = agricultural
# R = residential
# C = commercial
# O = other (open space, public, submerged)

# List of unknown codes:
#{'(WC)DOWNTOWN', 'RE', 'CCS', 'CEC', 'P', 'RZ5', 'CM(UV)', '(WC)COLLEGE', 'R2P', 'RAP',
# 'A2(PV)', 'LASED', 'R3(UV)', 'VARIOUS', 'CR(PKM)', 'ADP', 'PVSP', 'R1H1', '(WC)TOPANGA',
# 'PPSP', 'UC(CA)', 'M2(PV)', 'OS(PV)', 'LACFCD', '(WC)NORTHVILLAGE', 'C1(PV)', 'OS(UV)', 'CW',
# 'RAS3(UV)', '(WC)RIVER', 'GW(CA)', 'R1R3', '(WC)COMMERCE', 'R4P', 'C4(OX)', 'RSP', 'A1(UV)', 'R1V2',
# 'CM(GM)', 'R4(PV)', 'R5P', 'R1V1', 'C2(PV)', 'LAX', '(WC)UPTOWN', 'R3P', '(WC)PARK', 'R1V3',
# 'USC', # 'R1P', 'FRWY', 'PF(UV)', 'R3(PV)', 'M(PV)', 'UI(CA)', 'UV(CA)'}

def main():
    lonlat_pkl_path = 'supporting_files/lonlat_store.pkl'
    zoning_pkl_path = 'supporting_files/zoning_store.pkl'
    #file_name = 'supporting_files/ZONING_PLY.csv'
    file_name = 'supporting_files/test.csv'
    interface_url = "http://104.131.145.75/"




    zone_mapping = {'A1':'A', 'A2':'A', 'RA':'A', \
                    'RE40':'R', 'RE20':'R', 'RE15':'R', 'RE11':'R', 'RE9':'R', 'RS':'R', 'R1':'R', 'RU':'R', 'RZ2.5':'R', \
                    'RZ3':'R', 'RZ4':'R', 'RW1':'R', 'R2':'R', 'RD1.5':'R', 'RD2':'R', 'RD3':'R', 'RD4':'R', 'RD5':'R', \
                    'RD6':'R', 'RMP':'R', 'RW2':'R', 'R3':'R', 'RAS3':'R', 'R4':'R', 'RAS4':'R', 'R5':'R', \
                    'CR':'C', 'C1':'C', 'C1.5':'C', 'C2':'C', 'C4':'C', 'C5':'C', 'CM':'C', \
                    'MR1':'I', 'M1':'I', 'MR2':'I', 'M2':'I', 'M3':'I', \
                    'P':'P','PB':'P', \
                    'OS':'O', 'PF':'O', 'SL':'O', \
                    }

    t0 = time.time()
    if os.path.isfile(lonlat_pkl_path) and os.path.isfile(zoning_pkl_path):
        print("loading pickle files")
        lonlat_store = pickle.load( open( lonlat_pkl_path, "rb" ) )
        zoning_store = pickle.load( open( zoning_pkl_path, "rb" ) )
    else:
        # create mapping between GPS lon/lat and zoning code
        print("creating pickle files")
        num_lines = sum(1 for line in open(file_name)) - 1 # subtract 1 for header
        print("num_lines="+str(num_lines))
        lonlat_store = np.empty((num_lines,2))
        zoning_store = num_lines * [None]
        with open(file_name) as f:
            next(f)
            count = 0
            for line in f:
                zoning,area,length,lonlat = parse_line(line)
                lonlat_store[count][0] = lonlat[0]
                lonlat_store[count][1] = lonlat[1]
                zoning_store[count]    = zoning
                count += 1
        pickle.dump(lonlat_store, open( lonlat_pkl_path, "wb" ) )
        pickle.dump(zoning_store, open( zoning_pkl_path, "wb" ) )
    t1 = time.time()
    print(str(t1-t0) + " seconds to construct lon/lat")

    print(zoning_store)
    #unique = set(zoning_store)
    #print(unique)

    tree = scipy.spatial.cKDTree(lonlat_store, leafsize=100)
    t2 = time.time()
    print(str(t2-t1) + " seconds to construct tree")

    while(1):
        print(interface_url+"ImagePicker/metadata_zoning/")
        with urllib.request.urlopen(interface_url+"ImagePicker/metadata_zoning/") as url: # TODO: update to 104....
            try:
                data = json.loads(url.read().decode())
            except:
                print("no more")
                break
        print(data)
        pk = int(data['pk'])
        lon = float(data['lon'])
        lat = float(data['lat'])
        tmp = np.array([lon,lat])
        result = tree.query(tmp, k=1, eps=0, p=2, distance_upper_bound=.001)

        if result[0] == float('inf'):
            payload = {'pk':pk,'tag_text':'unknown'}
        else:
            payload = {'pk':pk,'tag_text':'zoning_store[result[1]]'}
        print(payload)
        post_url = interface_url + "ImagePicker/post_zoning/"
        r = requests.post(post_url, data={'json-str':json.dumps(payload)})
    t3 = time.time()
    print(str(t3-t2) + " seconds to run search")


    # possible annotations: {'C', 'P', 'A', 'I', 'O', 'U', 'R'}
    # C = commercial
    # P = parking
    # A = agricultural
    # R = residential
    # I = industrial
    # O = other (known)
    # U = unknown (unknown code or nearest neighbor too far away)
    #print("possible annotations: " + str(set(mappoint_zone_store)))
    #print("total map points = " + str(len(mappoint_zone_store)))
    #print("num residential = " + str(len([e for e in mappoint_zone_store if e == 'R'])))
    #print("num commercial = " + str(len([e for e in mappoint_zone_store if e == 'C'])))
    #print("num industrial = " + str(len([e for e in mappoint_zone_store if e == 'I'])))
    #print("num other = " + str(len([e for e in mappoint_zone_store if e == 'U'])))

if __name__ == '__main__':
    main()
