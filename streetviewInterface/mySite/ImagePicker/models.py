from django.db import models
from django.conf import settings

class MapPoint(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    photographerHeading = models.FloatField()
    panoID = models.TextField()

    def __str__(self):
        return str('lat='+str(self.latitude)+', long='+str(self.longitude)+', photographerHeading='+str(self.photographerHeading))


class StreetviewImage(models.Model):
    mapPoint = models.ForeignKey(MapPoint) # each mapPoint has two images corresponding to left and right
    heading = models.FloatField() # photographerHeading +- 90
    fov = models.IntegerField()
    pitch = models.FloatField()
    image = models.ImageField('img', upload_to=settings.MEDIA_ROOT)
