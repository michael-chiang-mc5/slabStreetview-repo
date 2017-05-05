from django.shortcuts import render
from django.http import HttpResponse
from .models import *

# Create your views here.
def index(request):
    context = {}
    return getHeading(request)
    #return render(request, 'ImagePicker/index4.html',context)

def save_image(request,latitude,longitude,heading,pitch):
    s = StreetviewImage(latitude=latitude, longitude=longitude, heading=heading, pitch=pitch)
    s.save()
    return HttpResponse('done')

def list(request):
    streetviewImages = StreetviewImage.objects.all()
    context = {'streetviewImages':streetviewImages}
    return render(request, 'ImagePicker/list.html', context)



# Given GPS coordinates, return the heading value perpendicular to the road
def getHeading(request):
    context = {}
    return render(request, 'ImagePicker/panorama.html',context)
