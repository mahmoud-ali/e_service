import csv
from datetime import datetime
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from gold_travel.models import AppMoveGold
from sswg.models import BasicFormExport, BasicFormExportCompany, CBSData, COCSData, CompanyDetails, CompanyDetailsEmtiaz, MOCSData, MmAceptanceData, ProductionCompany, SSMOData, SmrcNoObjectionData, TransferRelocationFormData
from workflow.data_utils import create_master_details_groups,create_model_groups
from sswg.admin import export,reexport,silver,export_emtiaz

from django.contrib.auth import get_user_model

admin_user = get_user_model().objects.get(id=1)

def create_groups():
    create_master_details_groups('sswg','basicformexport',export.report_main_class,export.report_inline_classes)
    create_master_details_groups('sswg','basicformexportcompany',export_emtiaz.report_main_class,export_emtiaz.report_inline_classes)
    create_master_details_groups('sswg','basicformreexport',reexport.report_main_class,reexport.report_inline_classes)
    create_master_details_groups('sswg','basicformsilver',silver.report_main_class,silver.report_inline_classes)

    #other apps 
    arr = [
        ('gold_travel','appmovegold'),
        ('gold_travel','appmovegolddetails'),
        ('gold_travel','lkpowner'),
        ('sswg','productioncompany'),
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

def create_app_groups():
    app = 'sswg'
    model_permissions = [
        {
            'group':'sswg_manager',
            'add':[], 
            'change':[], 
            'delete':[],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_secretary',
            'add':['BasicFormExport','BasicFormReExport','BasicFormSilver', 'TransferRelocationFormData'], 
            'change':['BasicFormExport','BasicFormReExport','BasicFormSilver', 'TransferRelocationFormData'], 
            'delete':['BasicFormExport','BasicFormReExport','BasicFormSilver'],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_economic_security',
            'add':[], 
            'change':['BasicFormExport','BasicFormReExport','BasicFormSilver'], 
            'delete':[],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_ssmo',
            'add':['SSMOData', 'CompanyDetails'], 
            'change':['BasicFormExport','BasicFormReExport','BasicFormSilver','SSMOData', 'CompanyDetails'], 
            'delete':[],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_smrc',
            'add':['SmrcNoObjectionData'], 
            'change':['BasicFormExport','BasicFormReExport','BasicFormSilver','SmrcNoObjectionData'], 
            'delete':[],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_mm',
            'add':['MmAceptanceData'], 
            'change':['BasicFormExport','BasicFormReExport','BasicFormSilver','MmAceptanceData'], 
            'delete':[],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },  
        {
            'group':'sswg_moc',
            'add':['MOCSData'], 
            'change':['BasicFormExport','BasicFormReExport','BasicFormSilver','MOCSData'], 
            'delete':[],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_coc',
            'add':['MOCSData'], 
            'change':['BasicFormExport','BasicFormReExport','BasicFormSilver','COCSData'], 
            'delete':[],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_military_intelligence',
            'add':[], 
            'change':['BasicFormExport','BasicFormReExport','BasicFormSilver',], 
            'delete':[],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_cbs',
            'add':['CBSData'], 
            'change':['BasicFormExport','BasicFormReExport','BasicFormSilver','CBSData'], 
            'delete':[],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
        },
        {
            'group':'sswg_custom_force',
            'add':[], 
            'change':['BasicFormExport','BasicFormReExport','BasicFormSilver',], 
            'delete':[],
            'view':['BasicFormExport','BasicFormReExport','BasicFormSilver','CompanyDetails', 'TransferRelocationFormData', 'SSMOData', 'SmrcNoObjectionData', 'MmAceptanceData', 'MOCSData', 'CBSData',], 
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

def import_gold_travel(row,main_obj_export=None,main_obj_reexport=None,main_obj_silver=None):
    if not (main_obj_export or main_obj_reexport or main_obj_silver):
        return False
    
    try:
        gold_travel_str = row[6].strip()
        if not gold_travel_str or gold_travel_str.startswith(('P', 'p')):
            return False

        gold_travel_list = list(map(lambda x: x.strip(), gold_travel_str.split('-')))

        gold_travel_qs = AppMoveGold.objects.filter(code__in=gold_travel_list)

        if gold_travel_qs.count() != len(gold_travel_list):
            print(f"Warning: Some gold travel codes not found for ID: {id}. Expected: {len(gold_travel_list)}, Found: {gold_travel_qs.count()}")
            return False

        for form_obj in gold_travel_qs:
            TransferRelocationFormData.objects.get_or_create(
                basic_form_export=main_obj_export,
                basic_form_reexport=main_obj_reexport,
                basic_form_silver=main_obj_silver,
                form=form_obj,
                raw_weight=form_obj.gold_weight_in_gram,
                allow_count=form_obj.gold_alloy_count,
                created_by=admin_user,
                updated_by=admin_user
            )

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

def import_ssmo(row,main_obj_export=None,main_obj_emtiaz=None,main_obj_reexport=None,main_obj_silver=None):
    if not (main_obj_export or main_obj_emtiaz or main_obj_reexport or main_obj_silver):
        return False
    
    try:
        ssmo_cert_no = row[11].strip()
        ssmo_raw_weight = float(row[12].strip())
        ssmo_net_weight = float(row[13].strip())
        ssmo_allow_count = int(row[7].strip())

        SSMOData.objects.get_or_create(
            basic_form_export=main_obj_export,
            basic_form_export_emtiaz=main_obj_emtiaz,
            basic_form_reexport=main_obj_reexport,
            basic_form_silver=main_obj_silver,
            certificate_id=ssmo_cert_no,
            raw_weight=ssmo_raw_weight,
            net_weight=ssmo_net_weight,
            allow_count=ssmo_allow_count,
            created_by=admin_user,
            updated_by=admin_user
        )

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

def import_mm_smrc(row,main_obj_export=None,main_obj_emtiaz=None,main_obj_reexport=None,main_obj_silver=None):
    if not (main_obj_export or main_obj_emtiaz or main_obj_reexport or main_obj_silver):
        return False
    
    try:
        mm_cert_no = row[14].strip()
        smrc_cert_no = row[15].strip()

        SmrcNoObjectionData.objects.get_or_create(
            basic_form_export=main_obj_export,
            basic_form_export_emtiaz=main_obj_emtiaz,
            basic_form_reexport=main_obj_reexport,
            basic_form_silver=main_obj_silver,
            cert_no=smrc_cert_no,
            created_by=admin_user,
            updated_by=admin_user
        )

        MmAceptanceData.objects.get_or_create(
            basic_form_export=main_obj_export,
            basic_form_export_emtiaz=main_obj_emtiaz,
            basic_form_reexport=main_obj_reexport,
            basic_form_silver=main_obj_silver,
            cert_no=mm_cert_no,
            created_by=admin_user,
            updated_by=admin_user
        )

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

def import_mocs(row,main_obj_export=None,main_obj_emtiaz=None,main_obj_reexport=None,main_obj_silver=None):
    if not (main_obj_export or main_obj_emtiaz or main_obj_reexport or main_obj_silver):
        return False
    
    try:
        mocs_contract_number = row[16].strip()
        mocs_registry_number = row[17].strip()
        mocs_unit_price = float(row[18].strip())
        # mocs_total_value = float(row[19].strip())
        mocs_port_of_shipment = row[20].strip()
        mocs_port_of_arrival = row[21].strip()
        mocs_main_bank_name = row[22].strip()
        mocs_subsidiary_bank_name = row[23].strip()

        MOCSData.objects.get_or_create(
            basic_form_export=main_obj_export,
            basic_form_export_emtiaz=main_obj_emtiaz,
            basic_form_reexport=main_obj_reexport,
            basic_form_silver=main_obj_silver,
            contract_number=mocs_contract_number,
            exporters_importers_registry_number=mocs_registry_number,
            unit_price_in_grams=mocs_unit_price,
            # total_contract_value=mocs_total_value,
            port_of_shipment=mocs_port_of_shipment,
            port_of_arrival=mocs_port_of_arrival,
            main_bank_name=mocs_main_bank_name,
            subsidiary_bank_name=mocs_subsidiary_bank_name,
            created_by=admin_user,
            updated_by=admin_user
        )

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

def import_cbs(row,main_obj_export=None,main_obj_emtiaz=None,main_obj_reexport=None,main_obj_silver=None):
    if not (main_obj_export or main_obj_emtiaz or main_obj_reexport or main_obj_silver):
        return False
    
    try:
        cbs_account_number = row[24].strip()
        cbs_ex_form_number = row[25].strip()
        cbs_issued_amount = row[26].strip()
        cbs_payment_method_str = row[27].strip()
        cbs_payment_method = 'transfer'

        if cbs_payment_method_str == 'دفع مقدم':
            cbs_payment_method = 'cash'
        
        CBSData.objects.get_or_create(
            basic_form_export=main_obj_export,
            basic_form_export_emtiaz=main_obj_emtiaz,
            basic_form_reexport=main_obj_reexport,
            basic_form_silver=main_obj_silver,
            customer_account_number=cbs_account_number,
            ex_form_number=cbs_ex_form_number,
            issued_amount=cbs_issued_amount,
            payment_method=cbs_payment_method,
            created_by=admin_user,
            updated_by=admin_user
        )
    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

def import_cf(row,main_obj_export=None,main_obj_emtiaz=None,main_obj_reexport=None,main_obj_silver=None):
    if not (main_obj_export or main_obj_emtiaz or main_obj_reexport or main_obj_silver):
        return False
    
    try:
        cf_cert_no = row[28].strip()
        cf_policy_no = row[29].strip()
        cf_dep_dt = datetime.strptime(row[30].strip(), "%m/%d/%Y").date()


        ###your code here
        return False

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

def import_tra_export(file_name='import_data.csv'):
    with open('./sswg/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            id = row[1].strip()

            try:

                date = datetime.strptime(row[2].strip(), "%m/%d/%Y").date()

                obj,_ = BasicFormExport.objects.get_or_create(
                    date = date,
                    sn_no = id,
                    created_by=admin_user,
                    updated_by=admin_user
                )

                
                if obj.state < 3 and import_gold_travel(row,main_obj_export=obj):
                    obj.state = 3
                    obj.save()
                else:
                    if obj.state == 1:
                        obj.delete()
                    continue

                if obj.state < 4 and import_ssmo(row,main_obj_export=obj):
                    obj.state = 4
                    obj.save()
                else:
                    continue

                if obj.state < 6 and import_mm_smrc(row,main_obj_export=obj):
                    obj.state = 6
                    obj.save()
                else:
                    continue

                if obj.state < 8 and import_mocs(row,main_obj_export=obj):
                    obj.state = 8
                    obj.save()
                else:
                    continue

                if obj.state < 9 and import_cbs(row,main_obj_export=obj):
                    obj.state = 9
                    obj.save()
                else:
                    continue

                if obj.state < 11 and import_cf(row,main_obj_export=obj):
                    obj.state = 11
                    obj.save()
                else:
                    continue

                #print(f"cf_cert_no: {cf_cert_no}, cf_policy_no: {cf_policy_no}, cf_dep_dt: {cf_dep_dt}")
                
                #print(f"Importing license with ID: {id}, Date: {date}, Gold Travel List: {gold_travel_list}")

                # Here you would typically create or update the model instance
            except Exception as e:
                print(f"Error importing license with ID: {id}. Error: {e}")

def delete_tra_export(sn_no):
    obj = BasicFormExport.objects.get(
        sn_no = sn_no,
    )

    CompanyDetails.objects.filter(
        basic_form_export=obj,
    ).delete()
    TransferRelocationFormData.objects.filter(
        basic_form_export=obj,
    ).delete()
    SSMOData.objects.filter(
        basic_form_export=obj,
    ).delete()
    SmrcNoObjectionData.objects.filter(
        basic_form_export=obj,
    ).delete()
    MmAceptanceData.objects.filter(
        basic_form_export=obj,
    ).delete()
    MOCSData.objects.filter(
        basic_form_export=obj,
    ).delete()
    COCSData.objects.filter(
        basic_form_export=obj,
    ).delete()
    CBSData.objects.filter(
        basic_form_export=obj,
    ).delete()
    obj.delete()
    print(f"Deleted BasicFormExport with sn_no: {sn_no}")
    return True
    
#############################

def import_emtiaz_company(row,main_obj_emtiaz):
    try:
        name = ProductionCompany.objects.get(id=row[33].strip())
        surrogate_name = row[10].strip()
        travel_cert_no = row[6].strip()
        total_weight = row[9].strip()
        total_count = row[7].strip()
        alloy_description = row[8].strip()
        
        CompanyDetailsEmtiaz.objects.get_or_create(
            basic_form_export_emtiaz=main_obj_emtiaz,
            name=name,
            surrogate_name=surrogate_name,
            surrogate_id_type=1,
            surrogate_id_val='',
            travel_cert_no=travel_cert_no,
            total_weight=total_weight,
            total_count=total_count,
            alloy_description=alloy_description,
            created_by=admin_user,
            updated_by=admin_user
        )
    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

def import_emtiaz_export(file_name='import_data_emtiaz.csv'):
    with open('./sswg/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            id = row[1].strip()

            try:

                date = datetime.strptime(row[2].strip(), "%m/%d/%Y").date()

                obj,_ = BasicFormExportCompany.objects.get_or_create(
                    date = date,
                    sn_no = id,
                    created_by=admin_user,
                    updated_by=admin_user
                )

                
                if obj.state < 3 and import_emtiaz_company(row,main_obj_emtiaz=obj):
                    obj.state = 3
                    obj.save()
                else:
                    if obj.state == 1:
                        obj.delete()
                    continue

                if obj.state < 4 and import_ssmo(row,main_obj_emtiaz=obj):
                    obj.state = 4
                    obj.save()
                else:
                    continue

                if obj.state < 6 and import_mm_smrc(row,main_obj_emtiaz=obj):
                    obj.state = 6
                    obj.save()
                else:
                    continue

                if obj.state < 8 and import_mocs(row,main_obj_emtiaz=obj):
                    obj.state = 8
                    obj.save()
                else:
                    continue

                if obj.state < 9 and import_cbs(row,main_obj_emtiaz=obj):
                    obj.state = 9
                    obj.save()
                else:
                    continue

                if obj.state < 11 and import_cf(row,main_obj_emtiaz=obj):
                    obj.state = 11
                    obj.save()
                else:
                    continue

                #print(f"cf_cert_no: {cf_cert_no}, cf_policy_no: {cf_policy_no}, cf_dep_dt: {cf_dep_dt}")
                
                #print(f"Importing license with ID: {id}, Date: {date}, Gold Travel List: {gold_travel_list}")

                # Here you would typically create or update the model instance
            except Exception as e:
                print(f"Error importing license with ID: {id}. Error: {e}")

def delete_emtiaz_export(sn_no):
    obj = BasicFormExportCompany.objects.get(
        sn_no = sn_no,
    )

    CompanyDetailsEmtiaz.objects.filter(
        basic_form_export=obj,
    ).delete()
    SSMOData.objects.filter(
        basic_form_export=obj,
    ).delete()
    SmrcNoObjectionData.objects.filter(
        basic_form_export=obj,
    ).delete()
    MmAceptanceData.objects.filter(
        basic_form_export=obj,
    ).delete()
    MOCSData.objects.filter(
        basic_form_export=obj,
    ).delete()
    COCSData.objects.filter(
        basic_form_export=obj,
    ).delete()
    CBSData.objects.filter(
        basic_form_export=obj,
    ).delete()
    obj.delete()
    print(f"Deleted BasicFormExport with sn_no: {sn_no}")
    return True
    
