from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from .models import SmallMining

class SmallMiningAdmin(LeafletGeoAdmin):
    model = SmallMining
    list_display = ["license_nu","company_name","state","mineral"]
    search_fields = ["license_nu","company_name","state","mineral"]

admin.site.register(SmallMining,SmallMiningAdmin)


