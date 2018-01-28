import math




def calculate_projected_line(image_fov,boundingBox,heading,lat,lon):
    distance = 70 # length of search line
    referencePixel = 960 # reference axis

    FOV = int(image_fov/2)
    signBoardPixelX1 = int(boundingBox[0])
    signBoardPixelX2 = int(boundingBox[1])
    avgSignBoardPixel = (signBoardPixelX1 + signBoardPixelX2)/2    #it is average pixel distance from the starting point of image
    distanceFromReferenceAxis = avgSignBoardPixel - referencePixel    #it is the distance of the avg sign board pixel from the reference axis
    anglePerPixel = FOV/(referencePixel) #it is to calculare angle value for 1 pixel
    angleSignBoard = round((anglePerPixel * distanceFromReferenceAxis),7)    #it is to calculate the angle of pixel from the google camera

    finalAngleValue = heading + angleSignBoard

    if float(finalAngleValue) > 359.9999999:
        AngleValue = round((float(finalAngleValue) - 360),7)
    else:
        AngleValue = round(float(finalAngleValue),7)

    # given in radians
    angle_projectedLine = math.radians(AngleValue)

    # TODO: I'm pretty sure this is wrong
    R = 6378.1 #Radius of the Earth
    d = float(distance) * 0.0003048 #Distance in km
    lat1 = math.radians(float(lat)) #Current lat point converted to radians
    lon1 = math.radians(float(lon)) #Current long point converted to radians
    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(angle_projectedLine))
    lon2 = lon1 + math.atan2(math.sin(angle_projectedLine)*math.sin(d/R)*math.cos(lat1),math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

    lat_projectedLine = lat2
    lon_projectedLine = lon2
    return lat_projectedLine, lon_projectedLine, angle_projectedLine
