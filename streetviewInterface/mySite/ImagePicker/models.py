from django.db import models
from django.conf import settings
from .dictionary_search import *


class CrawlerQueueEntry(models.Model):
    panoID = models.TextField()
    time = models.DateTimeField(auto_now_add=True)



class MapPoint(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    photographerHeading = models.FloatField()
    panoID = models.TextField(blank=True) # unstable across browser sessions
    tag = models.TextField(blank=True)
    num_links = models.IntegerField(null=True,blank=True)
    address = models.TextField(blank=True)
    neighbors = models.ManyToManyField("self")

    def __str__(self):
        return str('lat='+str(self.latitude)+', long='+str(self.longitude)+', photographerHeading='+str(self.photographerHeading))
    def serialize_csv(self):
        return str(self.pk)                      + '\t' + \
               str(self.latitude)                + '\t' + \
               str(self.longitude)               + '\t' + \
               str(self.photographerHeading)     + '\t' + \
               str(self.panoID)                  + '\t' + \
               str(self.tag)

class StreetviewImage(models.Model):
    mapPoint = models.ForeignKey(MapPoint) # each mapPoint has two images corresponding to left and right
    heading = models.FloatField() # photographerHeading +- 90
    fov = models.IntegerField()
    pitch = models.FloatField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return str("heading="+str(self.heading))
    def dimY(self):
        return self.image.height
    def dimX(self):
        return self.image.width
    def image_name(self):
        return str(self.pk) + '.jpg'
    def image_url(self):
        return settings.AWS_URL + self.image_name()

class BoundingBox(models.Model):
    streetviewImage = models.ForeignKey(StreetviewImage) # each image can have multiple bounding boxes
    method = models.TextField()
    x1 = models.IntegerField()
    x2 = models.IntegerField()
    y1 = models.IntegerField()
    y2 = models.IntegerField()
    score = models.FloatField(null=True, blank=True)
    is_nil = models.BooleanField(default=True)

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
        new_height = self.height()+20
        center_y  = (self.y2+self.y1)/2
        new_y1 = max(center_y - new_height/2,0)
        return new_y1
    def y2_expanded(self):
        new_height = self.height()+20
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
    def manualAnnotation(self):
        ocrText = OcrText.objects.filter(boundingBox=self).filter(method="manual")
        if len(ocrText) == 0:
            return None
        else:
            return ocrText[0]

    # benchmarks manual annotation against google ocr
    # Behavior:
    #   - There must be exactly 1 manual ocrText annotation otherwise
    #     language_manual = None
    #   - ocrText locale annotation must be one of [english, spanish, chinese, japanese, korean, thai] or else
    #     language_manual = other
    def benchmark(self):
        if self.method != 'google':
            raise ValueError('BoundingBox.benchmark can only be run on google-derived bounding boxes')

        # manual locale annotation
        ocrText_manual = OcrText.objects.filter(boundingBox=self).filter(method="manual")
        manual_locale = ocrText_manual[0].locale
        if manual_locale in ['english','spanish','chinese','japanese','korean','thai']:
            language_manual = manual_locale
        else:
            language_manual = 'other'

        # automatic google ocr annotation
        ocrText_ocr    = OcrText.objects.filter(boundingBox=self).filter(method="google")
        language_ocr    = ocrText_ocr[0].ocrlanguage_set.all()[0].language
        if language_ocr not in ['english','spanish','chinese','japanese','korean','thai']:
            language_ocr = 'other'

        # location tag
        try:
            tag = self.streetviewImage.mapPoint.tag
        except:
            tag = None

        # return
        return {'language_manual':language_manual,'language_ocr':language_ocr,'location':tag}

    def benchmark_deprecated(self):

        # manual locale annotation
        ocrText_manual = OcrText.objects.filter(boundingBox=self).filter(method="manual")
        if len(ocrText_manual) == 1:
            dictionary_manual = {'english':'english','spanish':'spanish', \
                                 'chinese':'chinese','japanese':'japanese', \
                                 'korean':'korean','thai':'thai'}
            manual_locale = ocrText_manual[0].locale
            try:
                language_manual = dictionary_manual[manual_locale]
            except:
                language_manual = 'other'
        else:
            language_manual = None

        # automatic google ocr annotation
        ocrText_ocr    = OcrText.objects.filter(boundingBox=self).filter(method="google")
        if len(ocrText_ocr) == 1:
            dictionary_ocr    = {'locale=en':'english','locale=es':'spanish', \
                                 'locale=zh':'chinese','locale=jp':'japanese', \
                                 'locale=ko':'korean' ,'locale=th':'thai'}
            ocr_locale    = ocrText_ocr[0].locale
            if 'locale=zh' in ocr_locale:
                ocr_locale = 'locale=zh'
            try:
                language_ocr = dictionary_ocr[ocr_locale]
            except:
                language_ocr = 'other'
        else:
            language_ocr = None

        # location tag
        try:
            tag = self.streetviewImage.mapPoint.tag
        except:
            tag = None

        # return
        return {'language_manual':language_manual,'language_ocr':language_ocr,'location':tag}

class OcrText(models.Model):
    boundingBox = models.ForeignKey(BoundingBox) # each image can have multiple bounding boxes
    method = models.TextField()
    text = models.TextField()
    locale = models.TextField(blank=True)
    score = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    def __str__(self):
        return str(self.method)+': '+str(self.text)

class OcrLanguage(models.Model):
    ocrText = models.ForeignKey(OcrText)
    language = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return 'BB_pk='+str(self.ocrText.boundingBox.pk) + ', ' + self.language
    def init(ocrText):
        ocr_text   = ocrText.text
        ocr_locale = ocrText.locale
        notes = ''
        if 'locale=zh' in ocr_locale: # possible "locale=zh-*"
            language = 'chinese'
        elif 'locale=jp' in ocr_locale:
            language = 'japanese'
        elif 'locale=ko' in ocr_locale:
            language = 'korean'
        elif 'locale=th' in ocr_locale:
            language = 'thai'
        elif 'locale=vi' in ocr_locale:
            language = 'vietnamese'
        # search across spanish/english dictionaries
        # en = english
        # es = spanish
        # da = danish
        # fil = filipino
        # pl = polish
        # nl = dutch
        # ms = malaysia
        # mt = maltese
        # it = italian
        # fr = french
        # fy = ???
        # uz = uzbek
        elif 'locale=en' in ocr_locale or \
             'locale=es' in ocr_locale or \
             'locale=da' in ocr_locale or \
             'locale=pl' in ocr_locale or \
             'locale=nl' in ocr_locale or \
             'locale=jv' in ocr_locale or \
             'locale=ms' in ocr_locale or \
             'locale=mt' in ocr_locale or \
             'locale=it' in ocr_locale or \
             'locale=fr' in ocr_locale or \
             'locale=fy' in ocr_locale or \
             'locale=uz' in ocr_locale or \
             'locale=co' in ocr_locale or \
             'locale=gl' in ocr_locale or \
             'locale=eu' in ocr_locale or \
             'locale=pt' in ocr_locale or \
             'locale=fil' in ocr_locale:
            best_language, notes = english_or_spanish(ocr_text)
            language = best_language
        else:
            language = 'other'
            best_match = ""
        ocrLanguage = OcrLanguage(ocrText=ocrText,language=language,notes=notes)
        ocrLanguage.save()
        return ocrLanguage


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
