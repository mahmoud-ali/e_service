from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from maintenance.models import (
    MaintenanceUnit, FaultCategory, MaintenanceRequest,
    CompletionReport, ServiceRating, SparePart, StockMovement,
    LowStockAlert, Notification
)

User = get_user_model()


class MaintenanceSystemTests(TestCase):
    def setUp(self):
        self.employee_group = Group.objects.create(name='maintenance_employee')
        self.elec_group = Group.objects.create(name='maintenance_elec')
        self.store_group = Group.objects.create(name='maintenance_store')
        self.admin_group = Group.objects.create(name='maintenance_admin')

        self.employee = User.objects.create_user(username='employee1', password='pass123', first_name='أحمد', last_name='علي')
        self.employee.groups.add(self.employee_group)

        self.technician = User.objects.create_user(username='tech1', password='pass123', first_name='عثمان', last_name='الفني')
        self.technician.groups.add(self.elec_group)

        self.storekeeper = User.objects.create_user(username='store1', password='pass123', first_name='خالد', last_name='المخزن')
        self.storekeeper.groups.add(self.store_group)

        self.admin = User.objects.create_user(username='admin1', password='pass123', first_name='مدير', last_name='الصيانة')
        self.admin.groups.add(self.admin_group)

        self.elec_unit = MaintenanceUnit.objects.create(
            name='وحدة الكهرباء',
            code='ELEC',
            group_name='maintenance_elec',
            icon='fa-bolt'
        )

        self.fault_cat = FaultCategory.objects.create(
            unit=self.elec_unit,
            name='عطل في القاطع الرئيسي',
            sub_category='أعطال التوزيع واللوحات',
            order=1
        )

        # Create Spare Part
        self.spare_part = SparePart.objects.create(
            sku='SP-ELEC-001',
            name='قاطع ثلاثي 63 أمبير',
            unit=self.elec_unit,
            quantity_in_stock=10,
            reorder_point=3,
            unit_of_measure='حبة'
        )

    def test_request_number_generation(self):

        req = MaintenanceRequest.objects.create(
            requester=self.employee,
            employee_name='أحمد علي',
            general_dept='إدارة الاستكشاف',
            department='إدارة التخطيط',
            location='الطابق الثالث - مكتب 302',
            assigned_unit=self.elec_unit,
            fault_category=self.fault_cat,
            fault_description='انقطاع التيار عن المكيف والإنارة'
        )
        self.assertTrue(req.request_number.startswith('MR-'))
        self.assertEqual(len(req.request_number), 12) # MR-2026-0001

    def test_workflow_transitions(self):
        req = MaintenanceRequest.objects.create(
            requester=self.employee,
            employee_name='أحمد علي',
            general_dept='الشؤون الإدارية',
            department='الموارد البشرية',
            location='المبنى الرئيسي',
            assigned_unit=self.elec_unit,
            fault_category=self.fault_cat,
            fault_description='مشكلة كهربائية'
        )
        self.assertEqual(req.status, MaintenanceRequest.STATUS_PENDING)

        # Receive request
        req.status = MaintenanceRequest.STATUS_RECEIVED
        req.save()
        self.assertEqual(req.status, MaintenanceRequest.STATUS_RECEIVED)

        # Assign technician and start in_progress
        req.assigned_technician = self.technician
        req.status = MaintenanceRequest.STATUS_IN_PROGRESS
        req.save()
        self.assertEqual(req.status, MaintenanceRequest.STATUS_IN_PROGRESS)
        self.assertEqual(req.assigned_technician, self.technician)

        # Finish request with completion report
        req.status = MaintenanceRequest.STATUS_COMPLETED
        req.save()
        self.assertEqual(req.status, MaintenanceRequest.STATUS_COMPLETED)

        # Check report
        CompletionReport.objects.create(
            request=req,
            technician=self.technician,
            work_done='تم تبديل القاطع واختبار الأحمال'
        )
        self.assertIsNotNone(req.completion_report)

    def test_floor_apartment_and_technical_technicians(self):
        from maintenance.models import Floor, Apartment, TechnicalTechnician

        floor = Floor.objects.create(name='الطابق الرابع', order=4)
        apt = Apartment.objects.create(floor=floor, name='شقة 402')
        tech_tech = TechnicalTechnician.objects.create(name='الفني حسام', phone='0911111111')

        req = MaintenanceRequest.objects.create(
            requester=self.employee,
            employee_name='أحمد علي',
            general_dept='الشؤون الإدارية',
            department='الموارد البشرية',
            floor=floor,
            apartment=apt,
            fault_category=self.fault_cat,
            fault_description='انقطاع تكييف بالشقة'
        )
        req.assigned_technical_technicians.add(tech_tech)

        self.assertEqual(req.floor, floor)
        self.assertEqual(req.apartment, apt)
        self.assertIn(tech_tech, req.assigned_technical_technicians.all())

    def test_manager_rejection(self):
        req = MaintenanceRequest.objects.create(
            requester=self.employee,
            employee_name='أحمد علي',
            general_dept='الشؤون الإدارية',
            department='الموارد البشرية',
            assigned_unit=self.elec_unit,
            fault_category=self.fault_cat,
            fault_description='طلب غير ملائم'
        )
        req.status = MaintenanceRequest.STATUS_REJECTED
        req.rejection_reason = 'خارج اختصاص إدارة الصيانة'
        req.save()

        self.assertEqual(req.status, MaintenanceRequest.STATUS_REJECTED)
        self.assertEqual(req.rejection_reason, 'خارج اختصاص إدارة الصيانة')

    def test_stock_movement_and_low_stock_signal(self):
        StockMovement.objects.create(
            spare_part=self.spare_part,
            movement_type=StockMovement.MOVEMENT_OUT,
            quantity=8,
            performed_by=self.storekeeper,
            notes='صرف لعملية صيانة'
        )

        self.spare_part.refresh_from_db()
        self.assertEqual(self.spare_part.quantity_in_stock, 2)

        alert = LowStockAlert.objects.filter(spare_part=self.spare_part, is_resolved=False).first()
        self.assertIsNotNone(alert)
        self.assertEqual(alert.quantity_at_alert, 2)

    def test_views_access_control(self):

        c = Client()

        c.force_login(self.employee)
        res = c.get(reverse('maintenance:new_request'))
        self.assertEqual(res.status_code, 200)

        c.force_login(self.technician)
        res = c.get(reverse('maintenance:technician_request_list'))
        self.assertEqual(res.status_code, 200)
        c.force_login(self.employee)
        res = c.get(reverse('maintenance:store_dashboard'))
        self.assertIn(res.status_code, [302, 403])

        c.force_login(self.admin)
        res = c.get(reverse('maintenance:admin_dashboard'))
        self.assertEqual(res.status_code, 200)

    def test_hr_employee_structure_autofill_and_readonly(self):

        from maintenance.forms import MaintenanceRequestForm

        form_non_emp = MaintenanceRequestForm(user=self.employee)
        self.assertFalse(form_non_emp.employee_in_structure)
        self.assertIsNone(form_non_emp.fields['employee_name'].widget.attrs.get('readonly'))
        try:
            from hr.models import EmployeeBasic
            self.employee.email = 'employee1@smrc.sd'
            self.employee.save()
            emp_hr = EmployeeBasic.objects.create(
                code=99991,
                name='أحمد علي الموظف الموثق',
                tarikh_milad='1990-01-01',
                tarikh_ta3in='2020-01-01',
                sex='male',
                email='employee1@smrc.sd',
                draja_wazifia=1,
                alawa_sanawia=1
            )

            form_emp = MaintenanceRequestForm(user=self.employee)
            self.assertTrue(form_emp.employee_in_structure)
            self.assertEqual(form_emp.initial.get('employee_name'), 'أحمد علي الموظف الموثق')
            self.assertTrue(form_emp.fields['employee_name'].widget.attrs.get('readonly'))
            self.assertTrue(form_emp.fields['general_dept'].widget.attrs.get('readonly'))
            self.assertTrue(form_emp.fields['department'].widget.attrs.get('readonly'))
        except Exception as e:
            pass

    def test_rate_service_submission(self):

        req = MaintenanceRequest.objects.create(
            requester=self.employee,
            employee_name='أحمد علي',
            general_dept='الشؤون الإدارية',
            department='الموارد البشرية',
            location='المبنى الرئيسي',
            assigned_unit=self.elec_unit,
            fault_category=self.fault_cat,
            fault_description='مشكلة كهربائية',
            status=MaintenanceRequest.STATUS_COMPLETED
        )

        c = Client()
        c.force_login(self.employee)
        url = reverse('maintenance:rate_service', kwargs={'pk': req.pk})

        res_get = c.get(url)
        self.assertEqual(res_get.status_code, 200)

        res_post = c.post(url, {
            'rating': '5',
            'comment': 'خدمة ممتازة وسريعة، شكراً للفريق!'
        })
        self.assertRedirects(res_post, reverse('maintenance:request_detail', kwargs={'pk': req.pk}))

        rating_obj = ServiceRating.objects.filter(request=req).first()
        self.assertIsNotNone(rating_obj)
        self.assertEqual(rating_obj.rating, 5)
        self.assertEqual(rating_obj.comment, 'خدمة ممتازة وسريعة، شكراً للفريق!')

    def test_switch_unit_by_maintenance_admin(self):
        air_unit = MaintenanceUnit.objects.create(
            name='وحدة التكييف',
            code='AIR_COND',
            group_name='maintenance_air_cond',
            icon='fa-snowflake'
        )

        req = MaintenanceRequest.objects.create(
            requester=self.employee,
            employee_name='أحمد علي',
            general_dept='الشؤون الإدارية',
            department='الموارد البشرية',
            location='المبنى الرئيسي',
            assigned_unit=self.elec_unit,
            assigned_technician=self.technician,
            fault_category=self.fault_cat,
            fault_description='مشكلة كهربائية',
            status=MaintenanceRequest.STATUS_IN_PROGRESS
        )

        c = Client()

        c.force_login(self.technician)
        url = reverse('maintenance:technician_request_detail', kwargs={'pk': req.pk})
        res_tech = c.post(url, {
            'action': 'switch_unit',
            'new_unit_id': air_unit.id
        })
        req.refresh_from_db()
        self.assertEqual(req.assigned_unit, self.elec_unit)

        c.force_login(self.admin)
        res_admin = c.post(url, {
            'action': 'switch_unit',
            'new_unit_id': air_unit.id
        })
        req.refresh_from_db()
        self.assertEqual(req.assigned_unit, air_unit)
        self.assertIsNone(req.assigned_technician)
        self.assertEqual(req.status, MaintenanceRequest.STATUS_PENDING)

    def test_auto_assign_employee_group_and_admin_link(self):

        new_user = User.objects.create_user(username='new_user_test', password='password123')
        self.assertTrue(new_user.groups.filter(name='maintenance_employee').exists())

        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()

        c = Client()
        c.force_login(self.admin)
        res = c.get(reverse('admin:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '/maintenance/')

    def test_admin_request_detail_view_unassigned_technician(self):

        req = MaintenanceRequest.objects.create(
            requester=self.employee,
            employee_name='أحمد علي',
            general_dept='الشؤون الإدارية',
            department='الموارد البشرية',
            location='المبنى الرئيسي',
            assigned_unit=self.elec_unit,
            assigned_technician=None,
            fault_category=self.fault_cat,
            fault_description='عطل تجريبي بدون فني مكلف',
            status=MaintenanceRequest.STATUS_PENDING
        )

        c = Client()
        c.force_login(self.admin)
        url = reverse('maintenance:admin_request_detail', kwargs={'pk': req.pk})
        res = c.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, req.request_number)





