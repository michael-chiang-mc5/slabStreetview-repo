from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import os
import urllib.request
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import ast
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from PIL import Image
from math import sqrt
from collections import Counter, defaultdict
from .google_ocr import *
import time
import sys
import subprocess
from random import randint
import json
import csv
import boto3
from random import randint
from time import sleep

def index_figures(request):
    sign_counts = MapPoint.count_zoning()
    sign_counts = sorted(sign_counts.items() , key=lambda x: x[1]['mean'], reverse=True)

    context = {'sign_counts':  sign_counts }
    return render(request, 'ImagePicker/index_figures.html',context)
