from django.contrib.auth import get_user_model

from bpmn_workflow.engine import BPMNEngine


user = get_user_model().objects.get(id=1)
data = {}

def runSample(obj):

    process_obj = BPMNEngine.start_process('needs_request_v1',obj, user)

    t1 = obj.get_current_tasks().last()

    while t1:
        print(f"id: {t1.id}, name: {t1}")
        BPMNEngine.complete_task(task_instance=t1,user=user,data=data)
        t1 = obj.get_current_tasks().last()


############ run ################
def t1():
    from bpmn_workflow.data import test

    from needs_request.models import NeedsRequest,Department

    obj = NeedsRequest.objects.create(date='2025-11-11',cause='test',department=Department.objects.first())
    print('***',obj)
    test.runSample(obj)
    obj.delete()