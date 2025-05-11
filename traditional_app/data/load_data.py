from pathlib import Path
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.utils import LayerMapping
from workflow.data_utils import create_master_details_groups
from traditional_app import admin,models

def create_groups():
    create_master_details_groups('traditional_app','dailyreport',admin.daily_report_main_class,admin.daily_report_inline_classes)

geo_root_path = Path(__file__).resolve().parent / "geo" 

layers = [
    # {
    #     "model": models.LkpSaigTmp,
    #     "filename": "AMM_Alsaagha.shp",
    #     "mapping": models.lkpsaigtmp_mapping,
    # },
    # {
    #     "model": models.LkpGrindinTmp,
    #     "filename": "AMM_GrindingMill.shp",
    #     "mapping": models.lkpgrindintmp_mapping,
    # },
    # {
    #     "model": models.LkpSougTmp,
    #     "filename": "AMM_Market.shp",
    #     "mapping": models.lkpsougtmp_mapping,
    # },
    # {
    #     "model": models.LkpSougOtherTmp,
    #     "filename": "AMM_Others.shp",
    #     "mapping": models.lkpsougothertmp_mapping,
    # },
    # {
    #     "model": models.LkpProductionTmp,
    #     "filename": "AMM_ProductionSite.shp",
    #     "mapping": models.lkpproductiontmp_mapping,
    # },
    # {
    #     "model": models.LkpProductionPathTmp,
    #     "filename": "AMM_ProductionSitePaths.shp",
    #     "mapping": models.lkpproductionpathtmp_mapping,
    # },
    # {
    #     "model": models.LkpSougServiceTmp,
    #     "filename": "AMM_Services.shp",
    #     "mapping": models.lkpsougservicetmp_mapping,
    # },
    # {
    #     "model": models.LkpSougWashingTmp,
    #     "filename": "AMM_WashingBasin.shp",
    #     "mapping": models.lkpsougwashingtmp_mapping,
    # },
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
        points_within_x_meter = poins_qs.annotate(
            location_srs=Transform('geom', srs)
        ).filter(
            location_srs__distance_lte=(
                Transform(poly.geom, srs),
                buffer  # meters
            )
        )

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
