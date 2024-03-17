from django.contrib.gis import admin
from .models import SmallMining

admin.site.register(SmallMining, admin.GISModelAdmin)


