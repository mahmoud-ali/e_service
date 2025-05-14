import csv

from pathlib import Path
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.utils import LayerMapping
from workflow.data_utils import create_master_details_groups, create_model_groups
from traditional_app import admin,models
from company_profile.models import LkpLocality

from django.contrib.auth import get_user_model

admin_user = get_user_model().objects.get(id=1)

def create_groups():
    app = 'traditional_app'

    create_master_details_groups(app,'dailyreport',admin.daily_report_main_class,admin.daily_report_inline_classes)

    arr = [
        'lkpsaig',
        'lkpmojam3attawa7in',
        'lkpsoag',
        'employee',
        'vehicle',
        'rentedapartment',
        'rentedvehicle',
        'lkp7ofrkabira',
        'lkp2bar',
        'lkp2jhizatbahth',
        'lkpsosalgold',
        'lkpgrabeel',
        'lkpkhalatat',
        'lkpsmallprocessingunit',
    ]

    for model_name in arr:
        print("Create groups for model",model_name)
        create_model_groups(app,model_name,{
            'groups':{
                'tra_state_manager':{
                    'permissions': {
                        '*': {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    },
                },
            },
        })

    return

#############################

geo_root_path = Path(__file__).resolve().parent / "geo" 

layers = [
    {
        "model": models.LkpSaigTmp,
        "filename": "AMM_Alsaagha.shp",
        "mapping": models.lkpsaigtmp_mapping,
    },
    {
        "model": models.LkpGrindinTmp,
        "filename": "AMM_GrindingMill.shp",
        "mapping": models.lkpgrindintmp_mapping,
    },
    {
        "model": models.LkpSougTmp,
        "filename": "AMM_Market.shp",
        "mapping": models.lkpsougtmp_mapping,
    },
    {
        "model": models.LkpSougOtherTmp,
        "filename": "AMM_Others.shp",
        "mapping": models.lkpsougothertmp_mapping,
    },
    {
        "model": models.LkpProductionTmp,
        "filename": "AMM_ProductionSite.shp",
        "mapping": models.lkpproductiontmp_mapping,
    },
    {
        "model": models.LkpProductionPathTmp,
        "filename": "AMM_ProductionSitePaths.shp",
        "mapping": models.lkpproductionpathtmp_mapping,
    },
    {
        "model": models.LkpSougServiceTmp,
        "filename": "AMM_Services.shp",
        "mapping": models.lkpsougservicetmp_mapping,
    },
    {
        "model": models.LkpSougWashingTmp,
        "filename": "AMM_WashingBasin.shp",
        "mapping": models.lkpsougwashingtmp_mapping,
    },
    {
        "model": models.LkpLocalityTmp,
        "filename": "Localities.shp",
        "mapping": models.lkplocalitytmp_mapping,
    },
]
def run(verbose=True):
    for layer in layers:
        layer["model"].objects.all().delete()
        lm = LayerMapping(layer["model"], geo_root_path / layer["filename"], layer["mapping"])
        lm.save(strict=True, verbose=verbose)

def point_within_polygon(poins_qs,polygon_qs,buffer,srs=32636):
    for poly in polygon_qs:
        if poly and poly.geom and poins_qs:
            points_within_x_meter = poins_qs.filter(geom__isnull=False) \
            .annotate(
                location_srs=Transform('geom', srs)
            ) \
            .filter(
                location_srs__distance_lte=(
                    Transform(poly.geom,srs),
                    buffer  # meters
                )
            )
            

            if points_within_x_meter:
                yield (poly,points_within_x_meter)

def polygon_within_polygon(polygon_small_qs,polygon_big_qs2):
    c = 0

    for poly_b in polygon_big_qs2:
        poly_s_qs = polygon_small_qs.filter(
            geom__intersects=poly_b.geom
        )

        if poly_s_qs.count() > 0:
            c += poly_s_qs.count()
            print("total",c)
            yield (poly_b.name,poly_s_qs.count()) #poly_b,poly_s_qs,

        
def xy_within_polygon(poins_qs,polygon_qs,field_name='geom'):
    for poly in polygon_qs:
        for pnt_obj in poins_qs:
            tmp_pnt = Point(pnt_obj.x,pnt_obj.y,srid=4326)
            if tmp_pnt.within(getattr(poly,field_name)):
                yield (poly,pnt_obj)
                break

if __name__ == '__main__':
    create_groups()

# from traditional_app.data import load_data
# from traditional_app import models

# a = load_data.point_within_polygon(models.LkpSaigTmp.objects.all(),models.LkpSougTmp.objects.all()[0:5],1000,32636)
# b = load_data.polygon_within_polygon(models.LkpSougTmp.objects.all(),models.LkpLocalityTmp.objects.all())
# print(a)

def load_locality_xy(file_name='locality_xy2.csv'):
    with open('./traditional_app/data/geo/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:

                id = float(row[0].strip())
                x = float(row[3].strip())
                y = float(row[4].strip())

                locality = LkpLocality.objects.get(id=id)
                tmp_pnt = Point(x,y,srid=4326)

                for poly in models.LkpLocalityTmp.objects.all():
                    if tmp_pnt.within(poly.geom):
                        poly.state = locality.state
                        poly.locality = locality
                        poly.save()
                        break

            except Exception as e:
                print(f'id: {id} Exception: {e}')

from django.contrib.gis.db.models.functions import Centroid

def get_locality_soug():
    """
    return locality with soug queryset pair
    """
    poins_qs = models.LkpSougTmp.objects.annotate(
        centroid=Centroid('geom'),
    )

    for poly in models.LkpLocalityTmp.objects.all():
        points_within_x_meter = poins_qs.filter(
            centroid__within=poly.geom
        )

        if poly and poly.locality and points_within_x_meter.exists():
            yield (poly.locality,points_within_x_meter)

def import_soug():
    for locality,soug_qs in get_locality_soug():
        print("locality",locality.name)
        for tmp_soug in soug_qs:
            print("soug",tmp_soug.name)
            yield models.LkpSoag.objects.create(
                name=tmp_soug.name,
                locality=locality,
                state=locality.state,
                geom=tmp_soug.geom,
                created_by=admin_user,
                updated_by=admin_user,
            )

def import_saig():
    models.LkpSaig.objects.all().delete()
    for soug,saig_qs in point_within_polygon(models.LkpSaigTmp.objects.all(),models.LkpSoag.objects.all(),1000):
        print("soug",soug.name)
        for tmp_saig in saig_qs:
            if soug:
                print("soug",tmp_saig.name)
                yield models.LkpSaig.objects.create(
                    soag=soug,
                    name=tmp_saig.name,
                    cordinates_x=tmp_saig.geom[0].x,
                    cordinates_y=tmp_saig.geom[0].y,
                    geom=tmp_saig.geom,
                    created_by=admin_user,
                    updated_by=admin_user,
                )

def import_mojam3_tawa7in():
    models.LkpMojam3atTawa7in.objects.all().delete()
    for soug,mojam3_qs in point_within_polygon(models.LkpGrindinTmp.objects.all(),models.LkpSoag.objects.all(),1000):
        print("soug",soug.name)
        for tmp_mojam3 in mojam3_qs:
            if soug:
                print("soug",tmp_mojam3.name)
                yield models.LkpMojam3atTawa7in.objects.create(
                    soag=soug,
                    owner_name=tmp_mojam3.mill_owner,
                    toa7in_jafa_count=1,
                    toa7in_ratiba_count=1,
                    cordinates_x=tmp_mojam3.geom[0].x,
                    cordinates_y=tmp_mojam3.geom[0].y,
                    geom=tmp_mojam3.geom,
                    created_by=admin_user,
                    updated_by=admin_user,
                )