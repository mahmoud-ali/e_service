from pa.models import TblCompanyCommitmentMaster

def get_company_details(commitment:TblCompanyCommitmentMaster):
    dict = {
        "name":commitment.company.name_ar,
        "address":commitment.company.address,
        "company_type":commitment.company.company_type,
    }

    if hasattr(commitment,'license'):
        dict['license'] = commitment.license

    if commitment.company.company_type == 'sageer':
        dict['license_count'] = commitment.company.tblcompanyproductionlicense_set.count()

    return dict
