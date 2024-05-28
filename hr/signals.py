def one_active_employee_bank_account(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].deactivate_other_accounts()

