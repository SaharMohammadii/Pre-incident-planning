from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from .utils import validate_phone_number
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import uuid


USER_ROLES = [
    ('staff', 'STAFF'),
    ('manager', 'MANAGER'),
    ('normal_user', "NORMAL_USER")
]

STAFF_STATUS = [
    ('no_status', 'NoStatus'),
    ('on_mission', 'OnMission'),
    # ('pending', 'Pending'),
    ('free', 'Free'),
]



class OTPBlackList(models.Model):
    otp_code = models.CharField(max_length=6)
    black_listed = models.BooleanField(default=True)

    def unblock_code(self):
        self.black_listed = False
        self.save()


class OTP(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)

    def is_valid(self):
        return self.created_at >= timezone.now() - timedelta(minutes=2)
    
    def __str__(self):
        return f"{self.user}"




class UserManager(BaseUserManager):
    def create_user(self, phone_number, otp_code=None, **extra_fields):
        if not phone_number:
            raise ValueError('The phone number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255, verbose_name='نام')
    last_name = models.CharField(max_length=255, verbose_name='نام خانوادگی')
    personnel_code = models.CharField(max_length=15, verbose_name="شماره پرسنلی")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    phone_number = models.CharField(
        max_length=11, unique=True, blank=True, null=True, validators=[validate_phone_number], verbose_name='شماره تلفن')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='تاریخ اولین ورود ')
    user_role = models.CharField(choices=USER_ROLES, default='staff', max_length=12)
    staff_status = models.CharField(choices=STAFF_STATUS, default="free", max_length=11)


    USERNAME_FIELD = 'phone_number'

    REQUIRED_FIELDS = ['first_name', 'last_name']
    PASSWORD_FIELD = None

    objects = UserManager()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"



    class Meta:
        verbose_name_plural = "اعضا"
        verbose_name = "عضو"

