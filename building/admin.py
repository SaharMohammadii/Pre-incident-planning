from django.contrib import admin

from .models import ImageHandler, Widget, Equipment, Floor, Building, Route

admin.site.register(Building)
admin.site.register(Floor)
admin.site.register(Equipment)
admin.site.register(Route)
admin.site.register(Widget)
admin.site.register(ImageHandler)

