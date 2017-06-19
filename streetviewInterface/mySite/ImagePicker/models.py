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
    nms = models.FloatField(default=1)

    def __str__(self):
        return str([self.x1, self.y1, self.x2, self.y2])
    def width(self):
        return self.x2 - self.x1
    def height(self):
        return self.y2 - self.y1
    def rescaled_x1(self):
        if self.method=="google":
            return self.x1
        else:
            new_width = self.width()*1.1
            center_x  = (self.x2+self.x1)/2
            new_x1 = max(center_x - new_width/2,0)
            return new_x1
    def rescaled_x2(self):
        if self.method=="google":
            return self.x2
        else:
            new_width = self.width()*1.1
            center_x  = (self.x2+self.x1)/2
            new_x2 = min(center_x + new_width/2,self.streetviewImage.dimX()-1)
            return new_x2


class OcrText(models.Model):
    boundingBox = models.ForeignKey(BoundingBox) # each image can have multiple bounding boxes
    method = models.TextField()
    text = models.TextField()
    notes = models.TextField(blank=True)
    def __str__(self):
        return str(self.method)+': '+str(self.text)

class ScriptIdentification(models.Model):
    boundingBox = models.ForeignKey(BoundingBox)
    method = models.TextField()
    languageID = models.IntegerField()
    score = models.FloatField()
    notes = models.TextField(blank=True)
    def __str__(self):
        return ""
    def language(self):
        if self.languageID == 1:
            return "arabic"
        elif self.languageID == 2:
            return "cambodian"
        elif self.languageID == 3:
            return "chinese"
        elif self.languageID == 4:
            return "english"
        elif self.languageID == 5:
            return "greek"
        elif self.languageID == 6:
            return "hebrew"
        elif self.languageID == 7:
            return "japanese"
        elif self.languageID == 8:
            return "kannada"
        elif self.languageID == 9:
            return "korean"
        elif self.languageID == 10:
            return "mongolian"
        elif self.languageID == 11:
            return "russian"
        elif self.languageID == 12:
            return "thai"
        elif self.languageID == 13:
            return "tibetan"
