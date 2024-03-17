from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from .models import SmallMining

smallmining_mapping1 = {
    'license_nu': 'License_nu',
    'company_name': 'COMPANY_NA',
    'state': 'state',
    'mineral': 'mineral',
    'valid': 'Valid',
    'end_date': 'End_date',
    'area': 'Area',
    'nots': 'Nots',
    'geom': 'POLYGON',
}

smallmining_mapping2 = {
    'company_name': 'Name',
    'geom': 'POLYGON',
}

smallmining_mapping3 = {
    'company_name': 'Name',
    'geom': 'POLYGON',
}

small_shp1 = Path(__file__).resolve().parent / "data" / "aaa.shp"
small_shp2 = Path(__file__).resolve().parent / "data" / "bbb.shp"
small_shp3 = Path(__file__).resolve().parent / "data" / "ccc.shp"

def run(verbose=True):
    lm = LayerMapping(SmallMining, small_shp1, smallmining_mapping1, transform=True)
    lm.save( verbose=verbose)

    lm = LayerMapping(SmallMining, small_shp2, smallmining_mapping2, transform=True)
    lm.save( verbose=verbose)

    lm = LayerMapping(SmallMining, small_shp3, smallmining_mapping3, transform=True)
    lm.save( verbose=verbose)