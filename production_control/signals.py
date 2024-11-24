def alloy_shipped(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].alloy_shipped() 