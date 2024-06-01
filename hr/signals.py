def one_active_employee_bank_account(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].deactivate_other_accounts()

def update_employee_social_data(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].update_number_of_children()
        kwargs['instance'].update_gasima_status()

def update_employee_moahil(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].update_moahil()

def delete_one_active_employee_bank_account(sender, **kwargs):
    kwargs['instance'].deactivate_other_accounts()

def delete_update_employee_social_data(sender, **kwargs):
    kwargs['instance'].update_number_of_children()
    kwargs['instance'].update_gasima_status()

def delete_update_employee_moahil(sender, **kwargs):
    kwargs['instance'].update_moahil()
