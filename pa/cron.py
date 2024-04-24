from .models import TblCompanyCommitmentSchedular

def generate_requests():
    for sch in TblCompanyCommitmentSchedular.objects.exclude(request_interval=TblCompanyCommitmentSchedular.INTERVAL_TYPE_MANUAL):
        sch.generate_request()