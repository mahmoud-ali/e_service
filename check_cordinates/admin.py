from django.contrib.gis import admin
from .models import SmallMining

class SmallMiningAdmin(admin.GISModelAdmin):
    model = SmallMining
    list_display = ["license_nu","company_name","state","mineral"]
    search_fields = ["license_nu","company_name","state","mineral"]

admin.site.register(SmallMining,SmallMiningAdmin)


