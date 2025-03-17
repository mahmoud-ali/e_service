from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def create_model_groups(app,model_name,model_attrs):
    """
    Create and assign permissions to model groups.

    This function creates groups and assigns permissions to them based on the 
    provided model attributes. It iterates through the groups specified in 
    `model_attrs` and assigns 'add', 'change', 'delete', and 'view' permissions 
    to each group if they are enabled.

    Args:
        app (str): The app label where the model is located.
        model_name (str): The name of the model.
        model_attrs (dict): A dictionary containing model attributes, including 
                            group information and permissions.

    Example:
        model_attrs = {
            'groups': [
                {
                    'name': 'group1',
                    'add': True,
                    'change': True,
                    'delete': False,
                    'view': True,
                },
                {
                    'name': 'group2',
                    'add': False,
                    'change': True,
                    'delete': True,
                    'view': True
                }
            ]
        }
        create_model_groups('my_app', 'MyModel', model_attrs)
    """
    # for group_attrs in model_attrs['groups']:
    #     group, created = Group.objects.get_or_create(name=group_attrs['name'])
    #     for perm_type in ['add', 'change', 'delete', 'view']:
    #         is_enabled = group_attrs[perm_type]
    #         if not is_enabled:
    #             continue
    #         model_name = model_name.lower()
    #         content_type = ContentType.objects.get(app_label=app, model=model_name)
    #         permission = Permission.objects.get(codename=perm_type+'_'+model_name, content_type=content_type)
    #         group.permissions.add(permission)

    for group_name,group_dict in model_attrs.get("groups").items():
        print(f"Get/Create group {group_name}")
        group, created = Group.objects.get_or_create(name=group_name)
        state_permissions = group_dict.get("permissions",{})
        user_perm = {'add': 0, 'change': 0, 'delete': 0, 'view': 0}
        for _,permissions in state_permissions.items():
            for perm in ['add', 'change', 'delete', 'view']:
                if perm in permissions and permissions[perm]:
                    user_perm[perm] = 1
                    continue

        for perm_type in user_perm.keys():
            if user_perm[perm_type]:
                model_name = model_name.lower()
                content_type = ContentType.objects.get(app_label=app, model=model_name)
                permission = Permission.objects.get(codename=perm_type+'_'+model_name, content_type=content_type)
                print(f"Add permission {permission}")
                group.permissions.add(permission)

def create_master_details_groups(app,main_model_name,main_model_attrs,inline_classes):
    """
    Create application groups for the main model and inline classes.

    This function creates model groups for the main model specified by 
    `main_model_name` and its attributes `main_model_attrs`. It also iterates 
    over the `inline_classes` dictionary to create model groups for each 
    inline class.

    Args:
        app: The application instance where the model groups will be created.
        main_model_name (str): The name of the main model.
        main_model_attrs (list): A list of attributes for the main model.
        inline_classes (dict): A dictionary where keys are model names and 
                                values are lists of attributes for each inline class.

    Returns:
        None
    """
    create_model_groups(app,main_model_name,main_model_attrs)

    for model_name, model_attrs in inline_classes.items():
        create_model_groups(app,model_name,model_attrs)