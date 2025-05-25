from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from workflow.data_utils import create_model_groups


def create_app_groups():
    app = 'sswg'
    model_permissions = [
        {
            'group':'sswg_manager',
            'add':[], 
            'change':[], 
            'delete':[],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_secretary',
            'add':['BasicForm', 'TransferRelocationFormData'], 
            'change':['BasicForm', 'TransferRelocationFormData'], 
            'delete':['BasicForm'],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_economic_security',
            'add':[], 
            'change':['BasicForm'], 
            'delete':[],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_ssmo',
            'add':['SSMOData', 'CompanyDetails'], 
            'change':['BasicForm','SSMOData', 'CompanyDetails'], 
            'delete':[],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_smrc',
            'add':['SmrcNoObjectionData'], 
            'change':['BasicForm','SmrcNoObjectionData'], 
            'delete':[],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_mm',
            'add':['MmAceptanceData'], 
            'change':['BasicForm','MmAceptanceData'], 
            'delete':[],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },  
        {
            'group':'sswg_moc',
            'add':['MOCSData'], 
            'change':['BasicForm','MOCSData'], 
            'delete':[],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_coc',
            'add':['MOCSData'], 
            'change':['BasicForm','COCSData'], 
            'delete':[],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_military_intelligence',
            'add':[], 
            'change':['BasicForm',], 
            'delete':[],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_cbs',
            'add':['CBSData'], 
            'change':['BasicForm','CBSData'], 
            'delete':[],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_custom_force',
            'add':[], 
            'change':['BasicForm',], 
            'delete':[],
            'view':['BasicForm','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
    ]

    for security_group in model_permissions:
        group, created = Group.objects.get_or_create(name=security_group['group'])
        for perm_type in ['add', 'change', 'delete', 'view']:
            for model in security_group[perm_type]:
                model = model.lower()
                content_type = ContentType.objects.get(app_label=app, model=model)
                permission = Permission.objects.get(codename=perm_type+'_'+model, content_type=content_type)
                group.permissions.add(permission)

    #other apps
    arr = [
        ('gold_travel','appmovegold'),
        ('gold_travel','appmovegolddetails'),
    ]

    groups = ['sswg_manager','sswg_secretary','sswg_economic_security','sswg_ssmo','sswg_smrc','sswg_mm','sswg_moc','sswg_coc','sswg_military_intelligence','sswg_cbs','sswg_custom_force',]

    for app,model_name in arr:
        print("Create groups for model",model_name)
        for g in groups:
            create_model_groups(app,model_name,{
                'groups':{
                    g:{
                        'permissions': {
                            '*': {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                        },
                    },
                },
            })