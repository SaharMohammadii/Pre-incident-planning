from django.contrib import admin
from .models import User



class UserAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'personnel_code', 'phone_number', 'date_joined', 'user_role', 'staff_status']
    fields = ['first_name', 'last_name', 'personnel_code', 'phone_number', 'user_role', 'staff_status']

    @admin.display(description='نام و نام خانوادگی')
    def get_name(self, obj):
        return obj.first_name + " " + obj.last_name

admin.site.register(User, UserAdmin)