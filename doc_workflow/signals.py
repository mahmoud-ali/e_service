def update_application_record_state_from_department_processing(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].app_record.goto_processing_executive() #instance = ApplicationDepartmentProcessing instance
        kwargs['instance'].add_executive_processing_record()

def update_application_record_state_from_executive_processing(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].department_processing.app_record.goto_delivery_ready() #instance = ApplicationExectiveProcessing instance

def update_application_record_state_from_delivery_ready(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].app_record.goto_delivery_complete() #instance = ApplicationDelivery instance
