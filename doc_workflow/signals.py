def update_application_record_state_from_department_processing(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].app_record.goto_processing_executive() #instance = ApplicationDepartmentProcessing instance

def update_application_record_state_from_executive_processing(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].department_processing.app_record.goto_delivery_ready() #instance = ApplicationExectiveProcessing instance
