from django.contrib import admin

from planning.models import CompanyInfoTask, CompanyLicenseInfoTask, CompanyProductionTask, ExportGoldCompanyTask, ExportGoldTraditionalTask, OtherMineralsTask, TraditionalProductionTask, TraditionalStateTask

############### Production #####################
class CompanyProductionTaskInline(admin.TabularInline):
    model = CompanyProductionTask
    extra = 1

class TraditionalProductionTaskInline(admin.TabularInline):
    model = TraditionalProductionTask
    extra = 1

class TraditionalStateTaskInline(admin.TabularInline):
    model = TraditionalStateTask
    extra = 1

class OtherMineralsTaskInline(admin.TabularInline):
    model = OtherMineralsTask
    extra = 1

class ExportGoldTraditionalTaskInline(admin.TabularInline):
    model = ExportGoldTraditionalTask
    extra = 1

class ExportGoldCompanyTaskInline(admin.TabularInline):
    model = ExportGoldCompanyTask
    extra = 1

class CompanyInfoTaskInline(admin.TabularInline):
    model = CompanyInfoTask
    extra = 1

class CompanyLicenseInfoTaskInline(admin.TabularInline):
    model = CompanyLicenseInfoTask
    extra = 1

