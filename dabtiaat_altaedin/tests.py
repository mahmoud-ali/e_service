from django.test import TestCase
from dabtiaat_altaedin.models import DabtiaatSetting, AppDabtiaat, AppDabtiaatDetails
from company_profile.models import LkpState
from django.contrib.auth import get_user_model

User = get_user_model()

class DabtiaatSettingTest(TestCase):
    def setUp(self):
        self.setting_active = DabtiaatSetting.objects.create(
            name="العوائد الجليلة",
            key="al3wayid_aljalila",
            percentage=10.0,
            calculation_base=DabtiaatSetting.BASE_TOTAL,
            is_active=True
        )
        self.setting_inactive = DabtiaatSetting.objects.create(
            name="الحافز",
            key="alhafiz",
            percentage=10.0,
            calculation_base=DabtiaatSetting.BASE_TOTAL,
            is_active=False
        )

    def test_get_percentage_active(self):
        self.assertEqual(DabtiaatSetting.get_percentage('al3wayid_aljalila', default=10.0), 10.0)

    def test_get_percentage_inactive_returns_zero(self):
        # Even though default is 10.0, since alhafiz exists and is_active=False, it must return 0.0
        self.assertEqual(DabtiaatSetting.get_percentage('alhafiz', default=10.0), 0.0)

    def test_get_percentage_missing_returns_default(self):
        self.assertEqual(DabtiaatSetting.get_percentage('non_existing_key', default=5.0), 5.0)

class AppDabtiaatCalculationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.state = LkpState.objects.create(name="الخرطوم", code="KRT", x=0.0, y=0.0)
        self.app = AppDabtiaat.objects.create(
            date="2026-01-01",
            source_state=self.state,
            created_by=self.user,
            updated_by=self.user
        )
        AppDabtiaatDetails.objects.create(
            app_dabtiaat=self.app,
            gold_weight_in_gram=100.0,
            gold_price=100.0
        )
        # sum_of_weight_multiply_price = 100 * 100 = 10000

    def test_inactive_setting_amount_is_zero(self):
        DabtiaatSetting.objects.create(
            name="العوائد الجليلة",
            key="al3wayid_aljalila",
            percentage=10.0,
            is_active=False
        )
        # al3wayid_aljalila is inactive, so its amount must be 0
        self.assertEqual(self.app.al3wayid_aljalila_amount, 0.0)

    def test_active_setting_amount(self):
        DabtiaatSetting.objects.create(
            name="العوائد الجليلة",
            key="al3wayid_aljalila",
            percentage=10.0,
            is_active=True
        )
        self.assertEqual(self.app.al3wayid_aljalila_amount, 1000.0)

    def test_admin_get_list_display_hides_inactive(self):
        from dabtiaat_altaedin.admin import AppDabtiaatAdmin
        from django.contrib.admin import AdminSite
        from django.test import RequestFactory

        DabtiaatSetting.objects.create(
            name="العوائد الجليلة",
            key="al3wayid_aljalila",
            percentage=10.0,
            is_active=False
        )
        admin_obj = AppDabtiaatAdmin(AppDabtiaat, AdminSite())
        request = RequestFactory().get('/')
        list_display = admin_obj.get_list_display(request)

        self.assertNotIn("al3wayid_aljalila_amount", list_display)

    def test_newly_added_setting_shows_in_list_display_and_calculates(self):
        from dabtiaat_altaedin.admin import AppDabtiaatAdmin
        from django.contrib.admin import AdminSite
        from django.test import RequestFactory

        new_setting = DabtiaatSetting.objects.create(
            name="رسوم بيئية",
            key="rasoom_beea",
            percentage=5.0,
            calculation_base=DabtiaatSetting.BASE_TOTAL,
            is_active=True
        )
        self.assertEqual(self.app.calculate_setting_amount(new_setting), 500.0)
        self.assertEqual(self.app.rasoom_beea_amount, 500.0)

        admin_obj = AppDabtiaatAdmin(AppDabtiaat, AdminSite())
        request = RequestFactory().get('/')
        list_display = admin_obj.get_list_display(request)

        self.assertIn("rasoom_beea_amount", list_display)
        display_func = getattr(admin_obj, "rasoom_beea_amount")
        self.assertEqual(display_func(self.app), "500")
        self.assertEqual(display_func.short_description, "رسوم بيئية")

    def test_newly_added_setting_without_key_auto_generates_key(self):
        from dabtiaat_altaedin.admin import AppDabtiaatAdmin
        from django.contrib.admin import AdminSite
        from django.test import RequestFactory

        new_setting = DabtiaatSetting.objects.create(
            name="رسوم خدمات",
            key="",
            percentage=2.0,
            calculation_base=DabtiaatSetting.BASE_TOTAL,
            is_active=True
        )
        self.assertTrue(new_setting.key.startswith("band_"))
        self.assertEqual(self.app.calculate_setting_amount(new_setting), 200.0)

        admin_obj = AppDabtiaatAdmin(AppDabtiaat, AdminSite())
        request = RequestFactory().get('/')
        list_display = admin_obj.get_list_display(request)

        expected_field = f"{new_setting.key}_amount"
        self.assertIn(expected_field, list_display)
        display_func = getattr(admin_obj, expected_field)
        self.assertEqual(display_func(self.app), "200")



