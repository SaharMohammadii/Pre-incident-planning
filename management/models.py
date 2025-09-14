from django.db import models
from django.contrib.auth import get_user_model
from building.models import Building
from .constants import WARNINGS, SAFETY_LEVELS, INSPECTION_STATUS
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import generate_inspection_code
import uuid
from django.contrib.gis.db import models as gis_models


User = get_user_model()



class Location(models.Model):

    lat = models.CharField(max_length=100, blank=True, null=True, verbose_name="Latitude")
    lang = models.CharField(max_length=100, blank=True, null=True, verbose_name="Langitude")
    alt = models.CharField(max_length=100, blank=True, null=True, verbose_name="altitude (elevation above sea level) (optional)")
    point = gis_models.PointField(geography=True, blank=True, null=True, spatial_index=True)


    def __str__(self):
        return f"{self.lat}, {self.lang}"
    

    def save(self, *args, **kwargs):
        if self.lat and self.lang:
            from django.contrib.gis.geos import Point
            try:
                self.point = Point(float(self.lang), float(self.lat))
            except ValueError:
                pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "موقعیت های مکانی"
        verbose_name = "موقعیت مکانی"


class FireStation(models.Model):

    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="نام آتش نشانی")
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="manager" ,blank=True, null=True, verbose_name="مدیر")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="موقعیت مکانی")
    staffs = models.ManyToManyField(User, blank=True, verbose_name="اعضای آتش نشانی")


    def __str__(self):
        return self.name


    class Meta:
        verbose_name_plural = "آتش نشانی ها"
        verbose_name = "آتش نشانی"

    

class Inspection(models.Model):

    building = models.ForeignKey(Building, on_delete=models.CASCADE, blank=True, null=True, verbose_name="ساختمان")
    inspection_created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ تعریف بازرسی")
    head_staff = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="head_staff", blank=True, null=True, verbose_name="مسئول بازرسان")
    staff = models.ManyToManyField(User, blank=True, verbose_name="بازرسان")
    
    warning_report = models.CharField(max_length=255, choices=WARNINGS, blank=True, null=True, verbose_name="سطوح هشدار و شدت خطر بالقوه")
    owner_report = models.CharField(max_length=255, choices=SAFETY_LEVELS, blank=True, null=True, verbose_name="سطوح ایمنی و اقدامات مالک/بهره بردار (اعتبار یکساله)")
    
    # when the inspection is completed the head staff can check this and then manager can approve it
    ready_to_review = models.BooleanField(default=False, verbose_name="بازدید انجام شده است")
    
    # when this field is checked, it indicates that the inpection is completed
    approved_by_manager = models.BooleanField(default=False, verbose_name="تایید شده توسط مدیر")
    status = models.CharField(choices=INSPECTION_STATUS, max_length=20, default="pending", blank=True, null=True, verbose_name="وضعیت بازرسی")
    fire_station = models.ForeignKey(FireStation, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="آتش نشانی بازرس")
    inspection_code = models.CharField(max_length=12, unique=True, blank=True, null=True, verbose_name="کد بازرسی")

    def __str__(self):
        return f"{self.fire_station} | {self.inspection_code}"
    

    class Meta:
        verbose_name_plural = "بازرسی ها"
        verbose_name = "بازرسی"


@receiver(post_save, sender=Inspection)
def replace_inspection_code(sender, instance, **kwargs):
    unqiue_code = ""
    found = False
    while not found:
        code = generate_inspection_code(length=12)
        inspection = Inspection.objects.filter(inspection_code=code)
        if not inspection.exists():
            found = True
            unqiue_code = code
            break
    
    instance.inspection_code = unqiue_code