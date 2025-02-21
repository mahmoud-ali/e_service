from django.test import TestCase
from sswg.models import BasicForm, SmrcNoObjectionData
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

class SmrcNoObjectionDataTests(TestCase):
    def setUp(self):
        self.basic_form = BasicForm.objects.create(
            date=timezone.now().date(),
            sn_no="TEST-001",
            created_by=None,
            updated_by=None
        )
        
        self.test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_smrc_no_objection_creation(self):
        obj = SmrcNoObjectionData.objects.create(
            basic_form=self.basic_form,
            smrc_no_objection_file=self.test_file
        )
        
        self.assertEqual(obj.basic_form.sn_no, "TEST-001")
        self.assertIn("test_file.pdf", obj.smrc_no_objection_file.name)
        self.assertTrue(obj.created_at)

    def test_attachment_path(self):
        obj = SmrcNoObjectionData.objects.create(
            basic_form=self.basic_form,
            smrc_no_objection_file=self.test_file
        )
        
        path = obj.attachment_path("test_file.pdf")
        self.assertIn(f"company_{self.basic_form.id}/sswg/", path)
        self.assertIn(str(timezone.now().date().strftime('%Y/%m/%d')), path)

    def test_string_representation(self):
        obj = SmrcNoObjectionData.objects.create(
            basic_form=self.basic_form,
            smrc_no_objection_file=self.test_file
        )
        self.assertEqual(str(obj), str(obj.id))

    def test_verbose_names(self):
        self.assertEqual(
            SmrcNoObjectionData._meta.verbose_name,
            "SSWG SmrcNoObjectionData"
        )
        self.assertEqual(
            SmrcNoObjectionData._meta.verbose_name_plural,
            "SSWG SmrcNoObjectionData"
        )
class MmAceptanceDataTests(TestCase):
    def setUp(self):
        self.basic_form = BasicForm.objects.create(
            date=timezone.now().date(),
            sn_no="TEST-002",
            created_by=None,
            updated_by=None
        )
        
        self.test_file = SimpleUploadedFile(
            "mm_acceptance.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_mm_acceptance_creation(self):
        obj = MmAceptanceData.objects.create(
            basic_form=self.basic_form,
            mm_aceptance_file=self.test_file
        )
        
        self.assertEqual(obj.basic_form.sn_no, "TEST-002")
        self.assertIn("mm_acceptance.pdf", obj.mm_aceptance_file.name)
        self.assertTrue(obj.created_at)

    def test_verbose_names(self):
        self.assertEqual(
            MmAceptanceData._meta.verbose_name,
            "SSWG MmAceptanceData"
        )
        self.assertEqual(
            MmAceptanceData._meta.verbose_name_plural,
            "SSWG MmAceptanceData"
        )

class MOCSDataTests(TestCase):
    def setUp(self):
        self.basic_form = BasicForm.objects.create(
            date=timezone.now().date(),
            sn_no="TEST-003",
            created_by=None,
            updated_by=None
        )
        
        self.test_file1 = SimpleUploadedFile(
            "mocs1.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        self.test_file2 = SimpleUploadedFile(
            "mocs2.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_mocs_data_creation(self):
        obj = MOCSData.objects.create(
            basic_form=self.basic_form,
            contract_number="CON-123",
            exporters_importers_registry_number="REG-456",
            unit_price_in_grams=50.0,
            total_contract_value=5000.0,
            port_of_shipment="Port A",
            port_of_arrival="Port B",
            main_bank_name="Main Bank",
            subsidiary_bank_name="Subsidiary Bank",
            contract_expiration_date=timezone.now().date() + timezone.timedelta(days=365),
            mocs1_file=self.test_file1,
            mocs2_file=self.test_file2
        )
        
        self.assertEqual(obj.contract_number, "CON-123")
        self.assertEqual(obj.unit_price_in_grams, 50.0)
        self.assertIn("mocs1.pdf", obj.mocs1_file.name)
        self.assertIn("mocs2.pdf", obj.mocs2_file.name)

class CBSDataTests(TestCase):
    def setUp(self):
        self.basic_form = BasicForm.objects.create(
            date=timezone.now().date(),
            sn_no="TEST-004",
            created_by=None,
            updated_by=None
        )
        
        self.test_file = SimpleUploadedFile(
            "cbs_report.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_cbs_data_creation(self):
        obj = CBSData.objects.create(
            basic_form=self.basic_form,
            customer_account_number="ACC-789",
            ex_form_number="EX-456",
            commercial_bank_name="Commercial Bank",
            issued_amount=timezone.now().date(),
            payment_method="transfer",
            cbs_file=self.test_file
        )
        
        self.assertEqual(obj.customer_account_number, "ACC-789")
        self.assertEqual(obj.payment_method, "transfer")
        self.assertIn("cbs_report.pdf", obj.cbs_file.name)
        self.assertEqual(str(obj), f"CBS-{obj.customer_account_number}")
