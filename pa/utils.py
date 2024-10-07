from company_profile.models import TblCompany

def get_company_types_from_groups(user):
    company_types = []

    if user.groups.filter(name="company_type_entaj").exists():
        company_types += [TblCompany.COMPANY_TYPE_ENTAJ]
    if user.groups.filter(name="company_type_mokhalfat").exists():
        company_types += [TblCompany.COMPANY_TYPE_MOKHALFAT]
    if user.groups.filter(name="company_type_emtiaz").exists():
        company_types += [TblCompany.COMPANY_TYPE_EMTIAZ]
    if user.groups.filter(name="company_type_sageer").exists():
        company_types += [TblCompany.COMPANY_TYPE_SAGEER]

    return company_types
