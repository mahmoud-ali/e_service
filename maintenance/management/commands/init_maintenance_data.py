"""
Management command لتهيئة البيانات الأولية لنظام الصيانة:
- وحدات الصيانة الأربع
- تصنيفات الأعطال حسب الاستمارة الرسمية
- مجموعات المستخدمين وصلاحياتهم

الاستخدام:
    python manage.py init_maintenance_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    help = 'تهيئة البيانات الأولية لنظام الصيانة'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('🔧 بدء تهيئة بيانات نظام الصيانة...'))

        self._create_units()
        self._create_fault_categories()
        self._create_groups()

        self.stdout.write(self.style.SUCCESS('✅ تم الإعداد بنجاح!'))

    # ─────────────────────────────────────────
    # وحدات الصيانة
    # ─────────────────────────────────────────
    def _create_units(self):
        from maintenance.models import MaintenanceUnit

        units_data = [
            {
                'code':       MaintenanceUnit.CODE_ELEC,
                'name':       'وحدة الكهرباء',
                'group_name': 'maintenance_elec',
                'icon':       '⚡',
            },
            {
                'code':       MaintenanceUnit.CODE_AIR_COND,
                'name':       'وحدة التبريد والتكييف',
                'group_name': 'maintenance_air_cond',
                'icon':       '❄️',
            },
            {
                'code':       MaintenanceUnit.CODE_MECH,
                'name':       'وحدة الميكانيكا',
                'group_name': 'maintenance_mech',
                'icon':       '🔩',
            },
            {
                'code':       MaintenanceUnit.CODE_CONST,
                'name':       'وحدة الإنشاءات',
                'group_name': 'maintenance_const',
                'icon':       '🏗️',
            },
            {
                'code':       MaintenanceUnit.CODE_SAFETY,
                'name':       'وحدة الأعمال الخطرة والسلامة',
                'group_name': 'maintenance_safety',
                'icon':       '🛡️',
                'requires_safety_permit': True,
            },
        ]

        for data in units_data:
            obj, created = MaintenanceUnit.objects.update_or_create(
                code=data['code'],
                defaults=data,
            )
            status = 'تم إنشاؤها' if created else 'موجودة مسبقاً'
            self.stdout.write(f"  {data['icon']} {data['name']}: {status}")

    # ─────────────────────────────────────────
    # تصنيفات الأعطال
    # ─────────────────────────────────────────
    def _create_fault_categories(self):
        from maintenance.models import MaintenanceUnit, FaultCategory

        ELEC     = MaintenanceUnit.objects.get(code=MaintenanceUnit.CODE_ELEC)
        AIR_COND = MaintenanceUnit.objects.get(code=MaintenanceUnit.CODE_AIR_COND)
        MECH     = MaintenanceUnit.objects.get(code=MaintenanceUnit.CODE_MECH)
        CONST    = MaintenanceUnit.objects.get(code=MaintenanceUnit.CODE_CONST)
        SAFETY   = MaintenanceUnit.objects.get(code=MaintenanceUnit.CODE_SAFETY)

        categories = [
            # ─── وحدة الكهرباء ELEC ───
            (ELEC, 'كهرباء عامة',           'الكهرباء العامة',                    1, False),
            (ELEC, 'كهرباء عامة',           'التوزيع الداخلي',                    2, False),
            (ELEC, 'كهرباء عامة',           'مفتاح التشغيل',                      3, False),
            (ELEC, 'كهرباء عامة',           'طبلون داخلي',                        4, False),
            (ELEC, 'كهرباء عامة',           'المفاتيح',                           5, False),
            (ELEC, 'الإضاءة',               'المروحة (سقف / شفاط)',               6, False),
            (ELEC, 'الإضاءة',               'شمعة الإضاءة',                       7, False),
            (ELEC, 'أخرى',                  'عطل مفتاح بنك',                      8, False),
            (ELEC, 'أخرى',                  'عطل ضغط الإدارة',                    9, False),

            # ─── وحدة التبريد والتكييف AIR_COND ───
            (AIR_COND, 'تكييف وتبريد',      'عدم التبريد',                        1, False),
            (AIR_COND, 'تكييف وتبريد',      'ضبط درجة البرودة',                   2, False),
            (AIR_COND, 'تكييف وتبريد',      'تسريب مياه (من التكييف)',            3, False),
            (AIR_COND, 'تكييف وتبريد',      'أخرى',                              4, False),

            # ─── وحدة الميكانيكا — سباكة MECH ───
            (MECH, 'سباكة',                 'تسريب مياه',                         1, False),
            (MECH, 'سباكة',                 'عطل حوض غسيل الأيدي',               2, False),
            (MECH, 'سباكة',                 'عطل الاستحمام (شور / بانيو)',        3, False),
            (MECH, 'سباكة',                 'أخرى',                              4, False),

            # ─── وحدة الميكانيكا — حدادة MECH ───
            (MECH, 'حدادة',                 'أعمال حدادة عامة',                   5, False),
            (MECH, 'حدادة',                 'درابزين البلكونات والشبابيك',        6, False),
            (MECH, 'حدادة',                 'سياج السلالم والممرات',              7, False),
            (MECH, 'حدادة',                 'أخرى',                              8, False),

            # ─── وحدة الإنشاءات — نجارة وأثاث CONST ───
            (CONST, 'نجارة',                'صيانة باب المدخل / البلكونة',        1, False),
            (CONST, 'نجارة',                'صيانة الخشب',                        2, False),
            (CONST, 'نجارة',                'شباك ألومنيوم',                      3, False),
            (CONST, 'نجارة',                'أخرى',                              4, False),

            # ─── وحدة الإنشاءات — أثاث CONST ───
            (CONST, 'أثاث',                 'صيانة أجلاس (ترابيزة / كرسي)',      5, False),
            (CONST, 'أثاث',                 'صيانة الدولاب',                     6, False),
            (CONST, 'أثاث',                 'فك وتركيب الأثاث',                  7, False),
            (CONST, 'أثاث',                 'أخرى',                              8, False),

            # ─── وحدة الإنشاءات — مباني CONST ───
            (CONST, 'مباني',                'صيانة أرضيات (مكاتب / هول / غرف / حمام)', 9, False),
            (CONST, 'مباني',                'ترميم / تكسير / تشطيب حوائط',      10, False),
            (CONST, 'مباني',                'أعمال نقاشة',                       11, False),
            (CONST, 'مباني',                'تغيير مكان الباب',                  12, False),
            (CONST, 'مباني',                'أخرى',                             13, False),

            # ─── وحدة الأعمال الخطرة والسلامة SAFETY ───
            (SAFETY, 'لحامات وقص',           'أعمال لحام وقص صاج ومعادن (خطر)',   1, True),
            (SAFETY, 'غازات وأبخرة',         'صيانة خطوط الغاز والمواد الكيميائية', 2, True),
            (SAFETY, 'ارتفاعات',            'أعمال صيانة بالواجهات والأماكن المرتفعة', 3, True),
            (SAFETY, 'إنشاءات خطرة',        'أعمال تكسير وبناء وإعادة هيكلة خطرة', 4, True),
        ]

        count = 0
        for unit, sub_cat, name, order, req_safety in categories:
            _, created = FaultCategory.objects.update_or_create(
                unit=unit, name=name,
                defaults={'sub_category': sub_cat, 'order': order, 'is_active': True, 'requires_safety_permit': req_safety}
            )
            if created:
                count += 1

        self.stdout.write(f"  📋 تصنيفات الأعطال: {count} جديد، {len(categories) - count} موجود")

    # ─────────────────────────────────────────
    # مجموعات المستخدمين
    # ─────────────────────────────────────────
    def _create_groups(self):
        groups_config = [
            ('maintenance_employee', 'موظف (مقدم طلب صيانة)'),
            ('maintenance_elec',     'فريق وحدة الكهرباء'),
            ('maintenance_air_cond', 'فريق وحدة التبريد والتكييف'),
            ('maintenance_mech',     'فريق وحدة الميكانيكا'),
            ('maintenance_const',    'فريق وحدة الإنشاءات'),
            ('maintenance_safety',   'قسم السلامة الداخلية'),
            ('maintenance_store',    'أمين مخزن قطع الغيار'),
            ('maintenance_admin',    'مدير إدارة الصيانة'),
        ]

        for group_name, description in groups_config:
            group, created = Group.objects.get_or_create(name=group_name)
            status = 'تم إنشاؤها' if created else 'موجودة'
            self.stdout.write(f"  👥 {description} [{group_name}]: {status}")

        # إضافة جميع المستخدمين بالنظام لمجموعة maintenance_employee
        from django.contrib.auth import get_user_model
        User = get_user_model()
        emp_group, _ = Group.objects.get_or_create(name='maintenance_employee')
        count = 0
        for user in User.objects.all():
            if not user.groups.filter(name='maintenance_employee').exists():
                user.groups.add(emp_group)
                count += 1
        self.stdout.write(f"  👤 تم إضافة {count} مستخدم موجود إلى مجموعة maintenance_employee.")

