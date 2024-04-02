from .models import TblCompanyCommitment

def generate_requests():
    for commitement in TblCompanyCommitment.objects.exclude(request_interval=TblCompanyCommitment.INTERVAL_TYPE_MANUAL):
        commitement.generate_request()