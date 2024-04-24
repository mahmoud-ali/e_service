def commitment_generate_request(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].generate_request() #instance = commitment instance

def send_email_after_add_request(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].send_email() #instance = request instance

def update_request_payment_state(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].request.update_payment_state() #instance = payment instance

