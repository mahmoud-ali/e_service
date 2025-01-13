from django.contrib import admin

from planning.models import CompanyInfoTask, CompanyLicenseInfoTask, CompanyMokhalafatTask, CompanyProductionTask, CompanySalamaMatlobatTask, Company7oadithTask, ExportGoldCompanyTask, ExportGoldTraditionalTask, OtherMineralsTask, Traditional7oadthTask, TraditionalProductionTask, TraditionalSalamaMatlobatTask, TraditionalSalamaRagabaTask, TraditionalStateTask, TraditionalTahsilByBandTask, TraditionalTahsilByJihaTask, TraditionalTahsilTask

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

############### Tahsil #####################
class TraditionalTahsilTaskInline(admin.TabularInline):
    model = TraditionalTahsilTask
    extra = 1

class TraditionalTahsilByBandTaskInline(admin.TabularInline):
    model = TraditionalTahsilByBandTask
    extra = 1

class TraditionalTahsilByJihaTaskInline(admin.TabularInline):
    model = TraditionalTahsilByJihaTask
    extra = 1

############### Salama #####################
class TraditionalSalamaMatlobatTaskInline(admin.TabularInline):
    model = TraditionalSalamaMatlobatTask
    extra = 1

class TraditionalSalamaRagabaTaskInline(admin.TabularInline):
    model = TraditionalSalamaRagabaTask
    extra = 1

class CompanySalamaMatlobatTaskInline(admin.TabularInline):
    model = CompanySalamaMatlobatTask
    extra = 1

class Company7oadithTaskInline(admin.TabularInline):
    model = Company7oadithTask
    extra = 1

class Traditional7oadthTaskInline(admin.TabularInline):
    model = Traditional7oadthTask
    extra = 1

class CompanyMokhalafatTaskInline(admin.TabularInline):
    model = CompanyMokhalafatTask
    extra = 1
