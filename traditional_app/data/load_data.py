from pathlib import Path

from django.contrib.gis.utils import LayerMapping

from workflow.data_utils import create_master_details_groups
from traditional_app import admin,models

def create_groups():
    create_master_details_groups('traditional_app','dailyreport',admin.daily_report_main_class,admin.daily_report_inline_classes)

if __name__ == '__main__':
    create_groups()

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

