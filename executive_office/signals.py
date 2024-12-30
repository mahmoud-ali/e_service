def update_inbox_state(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].inbox.update_inbox_state() #InboxTasks

def add_tasks_from_template(sender, **kwargs):
    if not kwargs['raw']:
        kwargs['instance'].add_tasks_from_template()  #Inbox