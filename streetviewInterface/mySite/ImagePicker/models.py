from django.db import models
from django.conf import settings

class MapPoint(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    photographerHeading = models.FloatField()
    panoID = models.TextField() # unstable across browser sessions
    def __str__(self):
        return str('lat='+str(self.latitude)+', long='+str(self.longitude)+', photographerHeading='+str(self.photographerHeading))
        #return self.panoID

class MapPointTag(models.Model):
    mapPoint = models.ForeignKey(MapPoint)
    tag = models.TextField()
    def __str__(self):
        return self.tag

class StreetviewImage(models.Model):
    mapPoint = models.ForeignKey(MapPoint) # each mapPoint has two images corresponding to left and right
    heading = models.FloatField() # photographerHeading +- 90
    fov = models.IntegerField()
    pitch = models.FloatField()
    image = models.ImageField('img', upload_to=settings.MEDIA_URL)

    def __str__(self):
        return str("heading="+str(self.heading))
    def dimY(self):
        return self.image.height
    def dimX(self):
        return self.image.width

class BoundingBox(models.Model):
    streetviewImage = models.ForeignKey(StreetviewImage) # each image can have multiple bounding boxes
    method = models.TextField()
    x1 = models.IntegerField()
    x2 = models.IntegerField()
    y1 = models.IntegerField()
    y2 = models.IntegerField()
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str([self.x1, self.y1, self.x2, self.y2])
    def width(self):
        return self.x2 - self.x1
    def height(self):
        return self.y2 - self.y1
    def x1_expanded(self):
        new_width = self.width()+75
        center_x  = (self.x2+self.x1)/2
        new_x1 = max(center_x - new_width/2,0)
        return new_x1
    def x2_expanded(self):
        new_width = self.width()+75
        center_x  = (self.x2+self.x1)/2
        new_x2 = min(center_x + new_width/2,self.streetviewImage.dimX()-1)
        return new_x2
    def y1_expanded(self):
        new_height = self.height()+15
        center_y  = (self.y2+self.y1)/2
        new_y1 = max(center_y - new_height/2,0)
        return new_y1
    def y2_expanded(self):
        new_height = self.height()+15
        center_y  = (self.y2+self.y1)/2
        new_y2 = min(center_y + new_height/2,self.streetviewImage.dimY()-1)
        return new_y2


    def googleOCR(self):
        ocrText = OcrText.objects.filter(boundingBox=self).filter(method="google")
        if len(ocrText) == 0:
            return None
        else:
            return ocrText[0]
    def crnnOCR(self):
        ocrText = OcrText.objects.filter(boundingBox=self).filter(method="crnn-lexiconFree")
        if len(ocrText) == 0:
            return None
        else:
            return ocrText[0]

class OcrText(models.Model):
    boundingBox = models.ForeignKey(BoundingBox) # each image can have multiple bounding boxes
    method = models.TextField()
    text = models.TextField()
    locale = models.TextField(blank=True)
    score = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    def __str__(self):
        return str(self.method)+': '+str(self.text)


#            0 "none"
#            1 "arabic"
#            2 "cambodian"
#            3 "chinese"
#            4 "english"
#            5 "greek"
#            6 "hebrew"
#            7 "japanese"
#            8 "kannada"
#            9 "korean"
#            10 "mongolian"
#            11 "russian"
#            12 "thai"
#            13 "tibetan"
