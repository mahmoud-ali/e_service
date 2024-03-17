# Created manualy by Mahmod on 2024-02-07 19:08

from django.db import migrations

def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    Group = apps.get_model("auth", "group")
    Group.objects.using(db_alias).bulk_create(
        [
            Group(name="pro_company_application_accept"),
            Group(name="pro_company_application_approve"),
            Group(name="company_type_entaj"),
            Group(name="company_type_mokhalfat"),
            Group(name="company_type_emtiaz"),
            Group(name="company_type_sageer"),

        ]
    )

    LkpCompanyProductionStatus = apps.get_model("company_profile", "lkpcompanyproductionstatus")
    LkpCompanyProductionStatus.objects.using(db_alias).bulk_create(
        [
            LkpCompanyProductionStatus(id=1, name="منتجة"),
            LkpCompanyProductionStatus(id=2, name="مقبلة"),
            LkpCompanyProductionStatus(id=2, name="استكشاف"),
            LkpCompanyProductionStatus(id=3, name="متوقفة"),
        ]
    )

    LkpCompanyProductionFactoryType = apps.get_model("company_profile", "lkpcompanyproductionfactorytype")
    LkpCompanyProductionFactoryType.objects.using(db_alias).bulk_create(
        [
            LkpCompanyProductionFactoryType(id=1, name="CIL"),
            LkpCompanyProductionFactoryType(id=2, name="CIC"),
            LkpCompanyProductionFactoryType(id=3, name="VAT"),
        ]
    )

    LkpCompanyProductionLicenseStatus = apps.get_model("company_profile", "lkpcompanyproductionlicensestatus")
    LkpCompanyProductionLicenseStatus.objects.using(db_alias).bulk_create(
        [
            LkpCompanyProductionLicenseStatus(id=1, name="ساري"),
            LkpCompanyProductionLicenseStatus(id=2, name="غير ساري"),
        ]
    )

class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0004_alter_tblcompanyproduction_email'),
    ]

    operations = [
        migrations.RunPython(forwards_func, migrations.RunPython.noop,atomic=False),
    ]
