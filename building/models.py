from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
import uuid
from FormCreator.models import FormResponse

FIRE_RISKS = [
    ('low', 'کم خطر'),
    ('moderate', 'میان خطر'),
    ('dangerous', "پرخطر"),
    ('very_dangerous', "بسیار پر خطر")
]

INCIDENT_RISKS = [
    ('unsafe', 'ناایمن'),
    ('low_safety', 'ایمنی پایین'),
    ('fairly_safe', 'نسبتا ایمن'),
]

EQUIPMENT_STATUS = [
    ('checked', 'مشاهده شد'),
    ('filled', 'پر شده است'),
    ('not_working', 'کار نمی‌کند'),
    ('out_dated', 'تاریخ گذشته'),
]

BUILDING_TYPE = [('tradeAssociations', 'واحد صنفی'),
                 ('accommodationUnit', 'واحد اقامتی'),
                 ('treatmentUnit', 'واحد درمانی'),
                 ('militaryUnit', 'واحد نظامی'),
                 ('residentialUnit', 'واحد مسکونی'),
                 ('businessUnit', 'واحد تجاری'),
                 ('industrialUnit', 'واحد صنعتی'),
                 ('administrativeUnit', 'واحد اداری'),
                 ('educationalUnit', 'واحد آموزشی'),
                 ('warehouse', 'انبار'),
                 ('other', 'سایر')]



class ImageUploader(models.Model):
    image = models.ImageField(upload_to='building/', blank=True, null=True, validators=[
                              FileExtensionValidator(allowed_extensions=['jpeg', 'jpg', 'png', 'webp', 'ico'])])
    
    description = models.CharField(max_length=255, blank=True, null=True)



class ImageHandler(models.Model):
    image = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)


class Widget(models.Model):

    name = models.CharField(max_length=255, blank=True, null=True)
    icon = models.URLField(max_length=500, blank=True, null=True)
    location = models.ForeignKey(
        "management.Location", on_delete=models.SET_NULL, blank=True, null=True)
    description = models.TextField(blank=True, null=True)


class Equipment(models.Model):

    widget = models.ForeignKey(Widget, on_delete=models.CASCADE, blank=True)
    status = models.CharField(choices=EQUIPMENT_STATUS,
                              max_length=12, blank=True, null=True)



class Route(models.Model):

    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    icon = models.URLField(max_length=500, blank=True, null=True)
    location = models.ForeignKey(
        "management.Location", on_delete=models.SET_NULL, blank=True, null=True)



class Floor(models.Model):
    widget = models.ManyToManyField(Widget, blank=True)
    order_of_floor = models.IntegerField(default=0, verbose_name="شماره طبقه")
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    images = models.ManyToManyField(
        ImageHandler, blank=True, verbose_name="عکس  های طبقه")

    equipments = models.ManyToManyField(Equipment, blank=True, related_name="equipments")

    # store locations of shape then draw it in the front-end
    shape = models.ManyToManyField('management.Location', blank=True)
    routes = models.ManyToManyField(Route, blank=True)



class Building(models.Model):
    owner_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="نام مالک")
    renewal_code = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="کد نوسازی")
    fire_risk = models.CharField(
        max_length=15, choices=FIRE_RISKS, blank=True, null=True, verbose_name="خطر حریق")
    incident_risk = models.CharField(
        max_length=12, choices=INCIDENT_RISKS, blank=True, null=True, verbose_name="خطر حادثه")
    permanant_residence = models.IntegerField(default=0, validators=[MinValueValidator(
        0)], blank=True, null=True, verbose_name="تعداد ساکنان دائمی")
    temp_residence = models.IntegerField(default=0, validators=[MinValueValidator(
        0)], blank=True, null=True, verbose_name="تعداد ساکنان موقت")
    is_building_tall = models.BooleanField(blank=True, null=True)
    width = models.FloatField(default=0.0, verbose_name="طول")
    height = models.FloatField(default=0.0, verbose_name="ارتفاع")
    length = models.FloatField(default=0.0, verbose_name="عرض")
    area = models.FloatField(default=0.0, verbose_name="مساحت")
    access_problem = models.TextField(
        blank=True, null=True, verbose_name="مشکلات دسترسی")
    description = models.TextField(
        blank=True, null=True, verbose_name="توضیحات")
    images = models.ManyToManyField(
        ImageHandler, blank=True, verbose_name="عکس های ساختمان")
    floors = models.ManyToManyField(Floor, blank=True)
    building_type = models.CharField(
        max_length=30, choices=BUILDING_TYPE, blank=True, null=True)
    location = models.ForeignKey(
        "management.Location", on_delete=models.SET_NULL, blank=True, null=True)
    routes = models.ManyToManyField(Route, blank=True, related_name="routes")
    safety_form = models.ForeignKey(FormResponse, on_delete=models.SET_NULL, blank=True, null=True, related_name="safety_form")
    safety_form_for_eco = models.ForeignKey(FormResponse, on_delete=models.SET_NULL, blank=True, null=True, related_name="safety_form_for_eco")



