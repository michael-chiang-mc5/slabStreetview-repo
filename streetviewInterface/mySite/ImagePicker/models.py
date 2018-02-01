from django.db import models
from django.conf import settings
from .dictionary_search import *
import requests
import statistics
import json
import ast

class ParcelBoundarySegment(models.Model):
    endpoint1_lat = models.FloatField() # A.x
    endpoint1_lng = models.FloatField() # A.y
    endpoint2_lat = models.FloatField() # B.x
    endpoint2_lng = models.FloatField() # B.y
    AIN = models.IntegerField()

    def __str__(self):
        return str(self.lnglat())

    def lnglat(self):
        return {'endpoint1_lat':self.endpoint1_lat, \
                'endpoint1_lng':self.endpoint1_lng, \
                'endpoint2_lat':self.endpoint2_lat, \
                'endpoint2_lng':self.endpoint2_lng, \
               }

    def A(self):
        return endpoint1_lat,endpoint1_lng
    def B(self):
        return endpoint2_lat,endpoint2_lng


class CrawlerQueueEntry(models.Model):
    panoID = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

class MapPoint(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    photographerHeading = models.FloatField() # 0 = north, 90 = E, 180 = S, 270 = W
    panoID = models.TextField(blank=True) # unstable across browser sessions
    tag = models.TextField(blank=True)
    num_links = models.IntegerField(null=True,blank=True)
    address = models.TextField(blank=True)
    neighbors = models.ManyToManyField("self")
    high_priority = models.BooleanField(default=False)


    def complete(self,lazy=None):
        """
        Set high_priority = True if any of the following is False:
            (1) Two associated streetview images
            (2) Streetview images set (i.e., downloaded)
            (3) CTPN run
            (4) Google OCR run

        lazy=True means we explicitly check whether images are saved in aws (this costs money)
        lazy=False is default. We do not check whether images are saved in aws (free)
        """

        if lazy is None:
            lazy=True
        else:
            lazy=False

        # make sure that there are two associated streetviewImage objects associated
        # with each mapPoint. If not, delete and recreate
        streetviewImages = self.streetviewimage_set.all()
        if len(streetviewImages)!=2:
            self.streetviewimage_set.all().delete()
            self.createStreetviewImages()
            print("MapPoint ",self.pk, " streetviewImage objects not set")
            return False,'streetview object'

        # check whether streetview images are set
        for streetviewImage in streetviewImages:
            if lazy:
                image_is_set = streetviewImage.check_if_image_is_set_lazy()
            else:
                image_is_set = treetviewImage.check_if_image_is_set()
            if image_is_set is False:
                print("MapPoint ",self.pk, " images not downloaded")
                return False,'image'

        # check whether CTPN is run
        for streetviewImage in streetviewImages:
            boundingBoxes = BoundingBox.objects.filter(streetviewImage=streetviewImage)
            if len(boundingBoxes)==0:
                print("MapPoint ",self.pk, " CTPN bounding box not generated")
                return False,'ctpn'

        # check whether google OCR is run
        for streetviewImage in streetviewImages:
            googleOCRs = GoogleOCR.objects.filter(streetviewImage=streetviewImage)
            if len(googleOCRs)==0:
                print("MapPoint ",self.pk, " googleOCR bounding box not generated")
                return False,'ocr'

        # set high_prioritity to false if two streetviewImage objects, images downloaded, CTPN run, and googleOCR run
        print("MapPoint ",self.pk, " data complete")
        return True,'complete'

    def count_language_total():
        # initailize output
        rn = {}
        for language in settings.OCR_LANGUAGES:
            rn[language] = 0

        #
        mapPoints = MapPoint.objects.filter(streetviewimage__googleocr__isnull=False)
        for mapPoint in mapPoints:
            count_language = mapPoint.count_language()
            for language in settings.OCR_LANGUAGES:
                rn[language] += count_language[language]
        return rn

    def count_language(self):
        streetviewImages = self.streetviewimage_set.all()

        # initailize output
        rn = {}
        for language in settings.OCR_LANGUAGES:
            rn[language] = 0

        # add up
        for streetviewImage in streetviewImages:
            count_language = streetviewImage.count_language()
            print("final result: " + str(count_language))
            for language in settings.OCR_LANGUAGES:
                rn[language] += count_language[language]

        # returnr
        return rn

    def get_census_tracts(self):
        censusBlocks = self.censusblock_set.all()
        tracts = []
        for block in censusBlocks:
            tracts.append(block.tract_code())
        unique = list(set(tracts)) # get unique
        #s = ",".join(unique)
        return unique[0]
    def __str__(self):
        return str('pk='+str(self.pk)+', lat='+str(self.latitude)+', long='+str(self.longitude)+', photographerHeading='+str(self.photographerHeading))
    def serialize_csv(self):
        return str(self.pk)                      + '\t' + \
               str(self.latitude)                + '\t' + \
               str(self.longitude)               + '\t' + \
               str(self.photographerHeading)     + '\t' + \
               str(self.panoID)                  + '\t' + \
               str(self.tag)
    def createStreetviewImages(self):
        self.streetviewimage_set.all().delete()
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
        # make sure there are two streetviewImage objects
        if len(self.streetviewimage_set.all()) != 2:
            return False
        # make sure images downloaded
        for streetviewImage in self.streetviewimage_set.all():
            if not streetviewImage.check_if_image_is_set_lazy():
                return False
        # 2 streetviewImage objects and images downloaded
        return True
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
        tags = MapTag.objects.filter(mapPoint=self,tag_type="zoning")
        if tags.count() == 1:
            return tags[0]
        else:
            raise ValueError('MapPoint ' +  str(self.pk)  +' does not have exactly one zoning tag (' +  str(tags.count()) + ' !=1)')

    def get_num_CTPN_boundingBoxes(self):
        num_boundingBoxes = BoundingBox.objects.filter(streetviewImage__mapPoint=self, is_nil=False, method="CTPN").distinct().count()
        return num_boundingBoxes

    def get_size_CTPN_boundingBoxes(self):
        boundingBoxes = BoundingBox.objects.filter(streetviewImage__mapPoint=self, is_nil=False, method="CTPN").distinct()
        total_area = 0
        for boundingBox in boundingBoxes:
            total_area += boundingBox.area()
        return total_area

    def get_CTPN_boundingBoxes(self):
        boundingBoxes = BoundingBox.objects.filter(streetviewImage__mapPoint=self, is_nil=False, method="CTPN").distinct()
        return boundingBoxes
    def get_GoogleOCR(self):
        googleOCRs = GoogleOCR.objects.filter(streetviewImage__mapPoint=self).distinct()
        return googleOCRs


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

class CensusBlock(models.Model):
    mapPoint = models.ForeignKey(MapPoint)
    fips = models.TextField()
    def __str__(self):
        return str(self.fips)
    def tract_code(self):
        state  = self.fips[0:2]
        county = self.fips[2:5]
        tract  = self.fips[5:11]
        block  = self.fips[11:]
        return state+county+tract

class StreetviewImage(models.Model):
    mapPoint = models.ForeignKey(MapPoint) # each mapPoint has two images corresponding to left and right
    heading = models.FloatField() # photographerHeading +- 90
    fov = models.IntegerField()
    pitch = models.FloatField()
    notes = models.TextField(blank=True)
    image_is_set = models.BooleanField(default=False)

    def get_left_or_right(self):
        if self.heading - self.mapPoint.photographerHeading < 0:
            return "left"
        else:
            return "right"

    def count_language(self):
        googleOCR = GoogleOCR.objects.get(streetviewImage=self)
        return googleOCR.count_language()

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
        return str("lon="+str(self.longitude)+", lat="+str(self.latitude))
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
    def image_url_if_exists(self):
        if self.image_is_set:
            return settings.AWS_URL + self.image_name()
        else:
            return "na"

    def check_if_image_is_set_lazy(self):
        if self.image_is_set == True:
            return True
        else:
            return False

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

class GoogleOCR(models.Model):
    streetviewImage = models.ForeignKey(StreetviewImage)
    json_text = models.TextField()
    def __str__(self):
        return self.json_text
    def json(self):
        s = self.json_text
        json_data = ast.literal_eval(s)
        return json_data[0]

    # helper function for words()
    def naive_words(self):
        data = self.json()
        if len(data)==0:
            return []


        blocks = data['fullTextAnnotation']['pages'][0]['blocks']
        rn = []
        for block in blocks:
            words = block['paragraphs'][0]['words']
            for word in words:
                boundingBox = GoogleOCR.sanitize_vertices(word['boundingBox']['vertices'])
                locale = word['property']['detectedLanguages'][0]['languageCode']
                if 'zh' in locale:
                    locale='zh'
                text = ""
                for symbol in word['symbols']:
                    text += symbol['text']
                rn.append({'text':text,'locale':locale,'boundingBox':boundingBox})
                #print(locale)
                #print(text)
                #print(boundingBox)
                #print("****")
        return rn

    def words(self):
        words = self.naive_words()
        rn = []
        for word in words:

            if word['locale'] not in settings.OCR_LANGUAGES:
               print("skipping due to locale: " + str(word))
               continue

            # exclude numbers
            skip = False
            for letter in word['text']:
                if letter in '1234567890':
                    skip = True
                    break
            if skip:
                print("skipping due to numbers: " + str(word))
                continue

            # append
            rn.append(word)
        return rn

    def count_language(self):
        words = self.words()
        rn = {}
        for language in settings.OCR_LANGUAGES:
            asdf = [e for e in words if e['locale'] == language]
            print(asdf)
            rn[language] = len(asdf)
        return rn

    def sanitize_vertices(vertices):
        tmp = {}
        for idx in range(0,4):
            tmp.update({idx: {}})
            for dim in ['x','y']:
                try:
                    val = vertices[idx][dim]
                except:
                    val = 0
                tmp[idx].update({dim:val})
        x1 = min(tmp[0]['x'], tmp[1]['x'], tmp[2]['x'], tmp[3]['x'])
        x2 = max(tmp[0]['x'], tmp[1]['x'], tmp[2]['x'], tmp[3]['x'])
        y1 = min(tmp[0]['y'], tmp[1]['y'], tmp[2]['y'], tmp[3]['y'])
        y2 = max(tmp[0]['y'], tmp[1]['y'], tmp[2]['y'], tmp[3]['y'])
        return [x1,x2,y1,y2]


class BoundingBox(models.Model):
    """
    CTPN bounding box
    """
    streetviewImage = models.ForeignKey(StreetviewImage) # each image can have multiple bounding boxes
    method = models.TextField()
    x1 = models.IntegerField()
    x2 = models.IntegerField()
    y1 = models.IntegerField()
    y2 = models.IntegerField()
    score = models.FloatField(null=True, blank=True)
    is_nil = models.BooleanField(default=False)

    def area(self):
        return self.width()*self.height()
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
