def update_inbox_state(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].inbox.update_inbox_state() 