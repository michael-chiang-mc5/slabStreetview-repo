from django.db import models
from django.conf import settings
from .dictionary_search import *
import requests
import statistics

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
    def createStreetviewImages(self):
        for rl in [{'heading':self.photographerHeading+90,'fov':35}, \
                    {'heading':self.photographerHeading-90,'fov':22.5}]:
            # save object
            streetviewImage = StreetviewImage(mapPoint=self, \
                                               heading=rl['heading'], \
                                               fov=rl['fov'], \
                                               pitch=0, \
                                               image_is_set=False, )
            streetviewImage.save()
    def images_set(self):
        all_images_set = True
        for streetviewImage in self.streetviewimage_set.all():
            if not streetviewImage.image_is_set:
                all_images_set = False
                break
        return all_images_set
    def count_zoning():
        total = MapPoint.objects.filter(maptag__tag_type="zoning").count()

        # initialize output
        possible_codes = list(MapTag.zone_mapping.keys())
        rn = {}
        for code in possible_codes:
            rn[code] = []

        # get mapPoints with: zoning tag, bounding box
        mapPoints = MapPoint.objects.filter(maptag__tag_type="zoning", streetviewimage__boundingbox__isnull=False).distinct()



        #return list(mapPoints.values_list('pk'))

        for mapPoint in mapPoints:
            zone_code =  mapPoint.get_zone_code()
            num_signs = mapPoint.get_num_signs()
            try:
                rn[zone_code].append(num_signs)
            except:
                rn['unknown'].append(num_signs)

        # rn2 example: {'C2' : {'mean':10.2,'std':0.3}, ...}
        rn2 = {}
        for key in list(rn.keys()):
            if len(rn[key]) == 0:
                rn2[key] = {'mean':-1, 'std':-1, 'n':0}
            else:
                rn2[key] = {'mean':sum(rn[key]) / len(rn[key]), 'std':statistics.stdev(rn[key]), 'n':len(rn[key])}
        return rn2




    def get_zone_code(self):
        try:
            return self.maptag_set.filter(tag_type="zoning")[0].tag_text
        except:
            return None
    def get_num_signs(self):
        streetviewImages = self.streetviewimage_set.all()
        count = 0
        for streetviewImage in streetviewImages:
            count += streetviewImage.count_boundingBoxes()
        return count

class MapTag(models.Model):
    mapPoint = models.ForeignKey(MapPoint)
    tag_type = models.TextField(blank=True)
    tag_text = models.TextField(blank=True) # "unknown" if MapPoint lon/lat not with 0.001 of any LARIAC data
    zone_mapping = {'A1':'A', 'A2':'A', 'RA':'A', \
                    'RE40':'R', 'RE20':'R', 'RE15':'R', 'RE11':'R', 'RE9':'R', 'RS':'R', 'R1':'R', 'RU':'R', 'RZ2.5':'R', \
                    'RZ3':'R', 'RZ4':'R', 'RW1':'R', 'R2':'R', 'RD1.5':'R', 'RD2':'R', 'RD3':'R', 'RD4':'R', 'RD5':'R', \
                    'RD6':'R', 'RMP':'R', 'RW2':'R', 'R3':'R', 'RAS3':'R', 'R4':'R', 'RAS4':'R', 'R5':'R', \
                    'CR':'C', 'C1':'C', 'C1.5':'C', 'C2':'C', 'C4':'C', 'C5':'C', 'CM':'C', \
                    'MR1':'I', 'M1':'I', 'MR2':'I', 'M2':'I', 'M3':'I', \
                    'P':'P','PB':'P', \
                    'OS':'O', 'PF':'O', 'SL':'O', \
                    'unknown':'U'}
    def __str__(self):
        return self.tag_text


class StreetviewImage(models.Model):
    mapPoint = models.ForeignKey(MapPoint) # each mapPoint has two images corresponding to left and right
    heading = models.FloatField() # photographerHeading +- 90
    fov = models.IntegerField()
    pitch = models.FloatField()
    notes = models.TextField(blank=True)
    image_is_set = models.BooleanField(default=False)

    def count_boundingBoxes(self):
        boundingBoxes = self.boundingbox_set.all()
        count = 0
        for boundingBox in boundingBoxes:
            if boundingBox.is_nil:
                continue
            else:
                count += 1
        return count

    def set_pending(self,trueOrFalse):
        if trueOrFalse is True:
            Pending.objects.filter(streetviewImage=self).delete()
            pending = Pending(streetviewImage=self)
            pending.save()
        else:
            Pending.objects.filter(streetviewImage=self).delete()
    def __str__(self):
        return str("heading="+str(self.heading))
    def valid_set():
        return StreetviewImage.objects.filter(pending__isnull=True)
    def dimY(self):
        return self.image.height
    def dimX(self):
        return self.image.width
    def image_name(self):
        return str(self.pk) + '.jpg'
    def image_url(self):
        return settings.AWS_URL + self.image_name()
    def check_if_image_is_set(self):
        request = requests.get(self.image_url())
        if request.status_code == 200:
            self.image_is_set = True
            self.save()
            print(str(self.pk) + " is set True")
            return True
        else:
            self.image_is_set = False
            self.save()
            print(str(self.pk) + " is set False")
            return False

class Pending(models.Model):
    streetviewImage = models.ForeignKey(StreetviewImage, null=True, blank=True,
                                        on_delete=models.CASCADE)
    is_corrupted = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)
    def remove_if_dead_task(self):
        time_elapse = datetime.datetime.utcnow().replace(tzinfo=utc) - self.time
        if time_elapse.total_seconds() > 86400 and is_corrupted is not False: # one day
            self.delete()

class BoundingBox(models.Model):
    streetviewImage = models.ForeignKey(StreetviewImage) # each image can have multiple bounding boxes
    method = models.TextField()
    x1 = models.IntegerField()
    x2 = models.IntegerField()
    y1 = models.IntegerField()
    y2 = models.IntegerField()
    score = models.FloatField(null=True, blank=True)
    is_nil = models.BooleanField(default=False)

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
