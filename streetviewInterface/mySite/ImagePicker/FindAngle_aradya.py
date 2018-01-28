import math
import geopy
from geopy.distance import VincentyDistance

def calculate_projected_line(image_fov,boundingBox,heading,lat_camera,lon_camera):
    distance = 70 # length of search line
    referencePixel = 960 # dimX / 2

    FOV = int(image_fov/2)
    signBoardPixelX1 = int(boundingBox[0])
    signBoardPixelX2 = int(boundingBox[1])
    avgSignBoardPixel = (signBoardPixelX1 + signBoardPixelX2)/2    #it is average pixel distance from the starting point of image
    distanceFromReferenceAxis = avgSignBoardPixel - referencePixel    # range = [-960,960]
    anglePerPixel = FOV/(referencePixel) #it is to calculare angle value for 1 pixel in degrees
    angleSignBoard = round((anglePerPixel * distanceFromReferenceAxis),7)    #it is to calculate the angle of pixel from the google camera

    angle_projectedLine = round((heading + angleSignBoard) % 360, 7) # 0 = N, 90 = E, 180 = S, 270 = W


    # given: lat1, lon1, b = bearing in degrees, d = distance in kilometers
    origin = geopy.Point(lat_camera, lon_camera)
    projected_line_endpoint = VincentyDistance(kilometers=1).destination(origin, angle_projectedLine)
    lat_projectedLine, lon_projectedLine = projected_line_endpoint.latitude, projected_line_endpoint.longitude

    return lat_projectedLine, lon_projectedLine, angle_projectedLine
