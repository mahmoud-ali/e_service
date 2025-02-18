from django.contrib import admin

from planning.forms import CompanyProductionEntagTaskForm,CompanyProductionSageerTaskForm
from planning.models import CompanyInfoTask, CompanyLicenseInfoTask, CompanyMokhalafatTask, \
    CompanyProductionTask, CompanySalamaMatlobatTask, Company7oadithTask, ExplorationMapTask, \
    ExportGoldCompanyTask, ExportGoldTraditionalTask, GMTask, Mas2oliaMojtama3iaTask, MediaDiscoveryTask, \
    MediaF2atMostakhdmaTask, MediaITSupportTask, MediaRasdBathTask, OtherMineralsTask, Traditional7oadthTask, \
    TraditionalProductionTask, TraditionalSalamaMatlobatTask, TraditionalSalamaRagabaTask, TraditionalStateTask, \
    TahsilByBandTask, TahsilByJihaTask, TraditionalTahsilTask

############### Production #####################
class CompanyProductionEntagTaskInline(admin.TabularInline):
    model = CompanyProductionTask
    form = CompanyProductionEntagTaskForm
    extra = 1

class CompanyProductionSageerTaskInline(admin.TabularInline):
    model = CompanyProductionTask
    form = CompanyProductionSageerTaskForm
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

class ExplorationMapTaskInline(admin.TabularInline):
    model = ExplorationMapTask
    extra = 1

############### Tahsil #####################
class TraditionalTahsilTaskInline(admin.TabularInline):
    model = TraditionalTahsilTask
    extra = 1

class TahsilByBandTaskInline(admin.TabularInline):
    model = TahsilByBandTask
    extra = 1

class TahsilByJihaTaskInline(admin.TabularInline):
    model = TahsilByJihaTask
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

############### Mojtam3ia #####################
class Mas2oliaMojtama3iaTaskInline(admin.TabularInline):
    model = Mas2oliaMojtama3iaTask
    extra = 1

############## Media #######################
class MediaRasdBathTaskInline(admin.TabularInline):
    model = MediaRasdBathTask
    extra = 1

class MediaF2atMostakhdmaTaskInline(admin.TabularInline):
    model = MediaF2atMostakhdmaTask
    extra = 1

class MediaDiscoveryTaskInline(admin.TabularInline):
    model = MediaDiscoveryTask
    extra = 1

############## IT #######################
class MediaITSupportTaskInline(admin.TabularInline):
    model = MediaITSupportTask
    extra = 1

################ GM #########################
class GMTaskInline(admin.TabularInline):
    model = GMTask
    extra = 1
