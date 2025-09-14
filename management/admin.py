from django.contrib import admin

from .models import FireStation, Location, Inspection

admin.site.register(FireStation)
admin.site.register(Location)
admin.site.register(Inspection)