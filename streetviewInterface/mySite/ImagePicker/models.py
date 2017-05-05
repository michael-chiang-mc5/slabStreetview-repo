from django.db import models

# Create your models here.
class StreetviewImage(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    heading = models.FloatField()
    pitch = models.FloatField()

    def __str__(self):
        return str('lat='+str(self.latitude)+', long='+str(self.longitude))
