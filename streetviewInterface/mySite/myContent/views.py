from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.
def index(request):
    return HttpResponseRedirect(reverse('ImagePicker:index'))
