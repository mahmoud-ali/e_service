from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from .models import OsmanState, SmallMining

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
    SmallMining.objects.all().delete()
    lm = LayerMapping(SmallMining, small_shp1, smallmining_mapping1, transform=True)
    lm.save( verbose=verbose)

    lm = LayerMapping(SmallMining, small_shp2, smallmining_mapping2, transform=True)
    lm.save( verbose=verbose)

    lm = LayerMapping(SmallMining, small_shp3, smallmining_mapping3, transform=True)
    lm.save( verbose=verbose)


def run_osman(verbose=True):
    state_shp1 = Path(__file__).resolve().parent / "data" / "osman" / "SR_State.shp"
    state_mapping1 = {
        'OBJECTID': 'OBJECTID',
        'scode': 'SCODE',
        'source': 'SOURCE',
        'name_arb': 'NAME_ARB',
        'state': 'STATE',
        'adm2_ne': 'ADM2_NE',
        'cnt_will_i': 'Cnt_WILL_I',
        'adm2_na': 'ADm2_NA',
        'adm2': 'ADM2',
        'smrc_amm_d': 'SMRC_AMM_D',
        'areakm2': 'AreaKm2',
        'areakm2z35': 'AreaKm2Z35',
        'shape_leng': 'SHAPE_Leng',
        'shape_area': 'SHAPE_Area',
        'shape': 'POLYGON',
    }

    OsmanState.objects.all().delete()
    lm = LayerMapping(OsmanState, state_shp1, state_mapping1)
    lm.save( verbose=verbose, strict=True)
