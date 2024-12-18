from company_profile.models import TblCompany


def get_company_types(request):
    company_types = []

    if request.user.groups.filter(name="company_type_entaj").exists():
        company_types += [TblCompany.COMPANY_TYPE_ENTAJ]
    if request.user.groups.filter(name="company_type_mokhalfat").exists():
        company_types += [TblCompany.COMPANY_TYPE_MOKHALFAT]
    if request.user.groups.filter(name="company_type_emtiaz").exists():
        company_types += [TblCompany.COMPANY_TYPE_EMTIAZ]
    if request.user.groups.filter(name="company_type_sageer").exists():
        company_types += [TblCompany.COMPANY_TYPE_SAGEER]

    return company_types
