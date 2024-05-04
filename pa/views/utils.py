from pa.models import TblCompanyCommitmentMaster

def get_company_details(commitment:TblCompanyCommitmentMaster):
    dict = {
        "name":commitment.company.name_ar,
        "address":commitment.company.address,
    }

    if hasattr(commitment,'license'):
        dict['license'] = commitment.license

    return dict
