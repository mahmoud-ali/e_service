from collections import defaultdict

from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import TblCompany
from .utils import get_app_metrics
                    
def in_progress_apps(request):
    if  '/managers/company_profile/' in request.path:
        data = []
        company_count = defaultdict(int)
        app_count = defaultdict(int)
        filter = []
        company_types = []

        if request.user.groups.filter(name="pro_company_application_accept").exists():
            filter += ["submitted"]
        if request.user.groups.filter(name="pro_company_application_approve").exists():
            filter += ["accepted"]

        if request.user.groups.filter(name="company_type_entaj").exists():
            company_types += [TblCompany.COMPANY_TYPE_ENTAJ]
        if request.user.groups.filter(name="company_type_mokhalfat").exists():
            company_types += [TblCompany.COMPANY_TYPE_MOKHALFAT]
        if request.user.groups.filter(name="company_type_emtiaz").exists():
            company_types += [TblCompany.COMPANY_TYPE_EMTIAZ]
        if request.user.groups.filter(name="company_type_sageer").exists():
            company_types += [TblCompany.COMPANY_TYPE_SAGEER]

        qs = get_app_metrics( \
            ['id','company','state','updated_at'], #fields
            {'state__in':filter,'company__company_type__in':company_types}, #filter
            ['company'], #select_related
            ["-updated_at"] #order_by
        )
        for r in qs:
            if r.app == 'Application: Fuel Permission' and r.state != 'submitted':
                continue
            key1 = r.company.__str__()
            company_count[key1] += 1 

            key2 = _(r.app)
            app_count[key2] += 1 

            data.append( {
                'id':r.id,
                'company': r.company.__str__(),
                'app': r.app,
                'updated_at': r.updated_at,
                'url': r.admin_url,
            })

        company_count = dict(sorted(company_count.items(),key=lambda x:x[1],reverse=True))
        app_count = dict(sorted(app_count.items(),key=lambda x:x[1],reverse=True))

        if data:
            return {
                'in_progress_apps': {
                    'data':data,
                    'summary':{
                        'company':{
                            'name': list(company_count.keys()),
                            'count': list(company_count.values())
                        },
                        'app':{
                            'name': list(app_count.keys()),
                            'count': list(app_count.values())
                        }
                    }
                }
            }
    
    return {}
