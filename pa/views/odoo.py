import time
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from company_profile.models import TblCompanyProduction, TblCompanyProductionLicense
from pa.models import TblCompanyRequestMaster, TblCompanyPaymentMaster, TblCompanyCommitmentMaster
from pa.odoo_sync import OdooSync
from django.utils.translation import gettext as _

@staff_member_required
def odoo_sync_view(request):
    if request.method == 'POST':
        def stream_progress():
            try:
                sync = OdooSync()
                yield f"data: <p class='info'>{_('Starting sync process...')}</p>\n\n"
                
                # Sync Companies
                companies = TblCompanyProduction.objects.all()
                yield f"data: <p class='info'>{_('Syncing %d companies...') % companies.count()}</p>\n\n"
                for comp in companies:
                    try:
                        sync.push_company(comp)
                        yield f"data: <p class='success'>{_('Synced company:')} {comp.name_ar}</p>\n\n"
                    except Exception as e:
                        yield f"data: <p class='error'>{_('Error syncing company')} {comp.name_ar}: {str(e)}</p>\n\n"
                    time.sleep(0.1)

                # Sync Licenses
                licenses = TblCompanyProductionLicense.objects.all()
                yield f"data: <p class='info'>{_('Syncing %d licenses...') % licenses.count()}</p>\n\n"
                for lic in licenses:
                    try:
                        sync.push_license(lic)
                        yield f"data: <p class='success'>{_('Synced license:')} {str(lic)}</p>\n\n"
                    except Exception as e:
                        yield f"data: <p class='error'>{_('Error syncing license')} {str(lic)}: {str(e)}</p>\n\n"
                    time.sleep(0.1)

                # Sync Commitments
                commitments = TblCompanyCommitmentMaster.objects.all()
                yield f"data: <p class='info'>{_('Syncing %d commitments...') % commitments.count()}</p>\n\n"
                for com in commitments:
                    try:
                        sync.push_commitment(com)
                        yield f"data: <p class='success'>{_('Synced commitment:')} {str(com)}</p>\n\n"
                    except Exception as e:
                        yield f"data: <p class='error'>{_('Error syncing commitment')} {str(com)}: {str(e)}</p>\n\n"
                    time.sleep(0.1)

                # Sync Requests
                requests = TblCompanyRequestMaster.objects.all()
                yield f"data: <p class='info'>{_('Syncing %d requests...') % requests.count()}</p>\n\n"
                for req in requests:
                    try:
                        sync.push_request(req)
                        yield f"data: <p class='success'>{_('Synced request:')} {str(req)}</p>\n\n"
                    except Exception as e:
                        yield f"data: <p class='error'>{_('Error syncing request')} {str(req)}: {str(e)}</p>\n\n"
                    time.sleep(0.1)

                # Sync Payments
                payments = TblCompanyPaymentMaster.objects.all()
                yield f"data: <p class='info'>{_('Syncing %d payments...') % payments.count()}</p>\n\n"
                for pay in payments:
                    try:
                        sync.push_payment(pay)
                        yield f"data: <p class='success'>{_('Synced payment:')} {str(pay)}</p>\n\n"
                    except Exception as e:
                        yield f"data: <p class='error'>{_('Error syncing payment')} {str(pay)}: {str(e)}</p>\n\n"
                    time.sleep(0.1)

                yield f"data: <p class='done'>{_('Sync process completed.')}</p>\n\n"
            except Exception as e:
                yield f"data: <p class='error'>{_('Sync failed:')} {str(e)}</p>\n\n"

        return StreamingHttpResponse(stream_progress(), content_type='text/event-stream')
    
    return render(request, 'pa/odoo_sync_progress.html')
