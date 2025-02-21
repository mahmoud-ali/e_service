import datetime

from django.test import TestCase
from sswg.models import BasicForm, CompanyDetails, TransferRelocationFormData, SSMOData, SmrcNoObjectionData, MOCSData,CBSData, MOCSData, MmAceptanceData, SmrcNoObjectionData
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
from company_profile.models import LkpState
from gold_travel.models import LkpOwner, AppMoveGold

User = get_user_model()

class SSWGModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )

        self.state = LkpState.objects.create(
            name="Khartoum"
        )
        self.owner = LkpOwner.objects.create(
            name='Test Owner',
        )
        self.move_gold = AppMoveGold.objects.create(
            date = datetime.date.today(),
            owner_name_lst=self.owner,
            owner_address='company address',
            repr_name='Hassan Omer',
            repr_address='Hassan address',
            repr_phone='09355555555',
            repr_identity_type=1,
            repr_identity='p123123',
            repr_identity_issue_date= datetime.date.today(),
            source_state=self.state,
            created_by=self.user,
            updated_by=self.user
        )

    def test_basic_form_creation(self):
        basic_form = BasicForm.objects.create(
            date=datetime.date.today(),
            sn_no='SSWG-001',
            state=BasicForm.STATE_1,
            created_by=self.user,
            updated_by=self.user
        )
        self.assertEqual(basic_form.sn_no, 'SSWG-001')
        self.assertEqual(basic_form.state, BasicForm.STATE_1)
        self.assertEqual(basic_form.date, datetime.date.today())

    def test_company_details_relationship(self):
        basic_form = BasicForm.objects.create(
            date=datetime.date.today(),
            sn_no='SSWG-002',
            created_by=self.user,
            updated_by=self.user
        )
        
        company_details = CompanyDetails.objects.create(
            name=self.owner,
            surrogate_name='Test Surrogate',
            surrogate_id_type=AppMoveGold.IDENTITY_PASSPORT,
            surrogate_id_val='PASS123',
            surrogate_id_phone='+249123456789',
            basic_form=basic_form,
            created_by=self.user,
            updated_by=self.user
        )
        self.assertEqual(company_details.basic_form, basic_form)
        self.assertIn('Test Surrogate', str(company_details))

    def test_smrc_data_signal_creation(self):
        basic_form = BasicForm.objects.create(
            date=datetime.date.today(),
            sn_no='SSWG-003',
            created_by=self.user,
            updated_by=self.user
        )
        
        TransferRelocationFormData.objects.create(
            form=self.move_gold,
            basic_form=basic_form,
            smrc_file=SimpleUploadedFile('test.pdf', b'content'),
            created_by=self.user,
            updated_by=self.user
        )
        
        # Verify automatic company details creation through signal
        company_details = CompanyDetails.objects.get(basic_form=basic_form)
        self.assertEqual(company_details.surrogate_name, self.move_gold.repr_name)
        self.assertEqual(company_details.surrogate_id_val, self.move_gold.repr_identity)

    def test_full_workflow(self):
        # Create basic form
        basic_form = BasicForm.objects.create(
            date=datetime.date.today(),
            sn_no='SSWG-004',
            created_by=self.user,
            updated_by=self.user
        )
        
        # Create all related records
        TransferRelocationFormData.objects.create(
            form=self.move_gold,
            basic_form=basic_form,
            smrc_file=SimpleUploadedFile('smrc.pdf', b'content'),
            created_by=self.user,
            updated_by=self.user
        )
        
        SSMOData.objects.create(
            raw_weight=95.0,
            net_weight=90.0,
            allow_count=5,
            certificate_id='CERT-001',
            basic_form=basic_form,
            ssmo_file=SimpleUploadedFile('ssmo.pdf', b'content'),
            created_by=self.user,
            updated_by=self.user
        )
        
        MOCSData.objects.create(
            contract_number='CON-001',
            exporters_importers_registry_number='REG-001',
            unit_price_in_grams=50.0,
            total_contract_value=5000.0,
            port_of_shipment='Port Sudan',
            port_of_arrival='Jeddah',
            main_bank_name='Bank of Sudan',
            subsidiary_bank_name='Sudan Subsidiary Bank',
            contract_expiration_date=datetime.date.today() + datetime.timedelta(days=365),
            basic_form=basic_form,
            mocs1_file=SimpleUploadedFile('contract.pdf', b'content'),
            mocs2_file=SimpleUploadedFile('cert.pdf', b'content'),
            created_by=self.user,
            updated_by=self.user
        )
        
        # Verify all relationships
        self.assertEqual(basic_form.smrc_data.form, self.move_gold)
        self.assertEqual(basic_form.ssmo_data.certificate_id, 'CERT-001')
        self.assertEqual(basic_form.mocs_data.contract_number, 'CON-001')


class SmrcNoObjectionDataTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )

        self.basic_form = BasicForm.objects.create(
            date=timezone.now().date(),
            sn_no="TEST-001",
            created_by=self.user,
            updated_by=self.user
        )
        
        self.test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_smrc_no_objection_creation(self):
        obj = SmrcNoObjectionData.objects.create(
            basic_form=self.basic_form,
            smrc_no_objection_file=self.test_file,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(obj.basic_form.sn_no, "TEST-001")
        self.assertIn("test_file", obj.smrc_no_objection_file.name)
        self.assertTrue(obj.created_at)

    def test_attachment_path(self):
        obj = SmrcNoObjectionData.objects.create(
            basic_form=self.basic_form,
            smrc_no_objection_file=self.test_file,
            created_by=self.user,
            updated_by=self.user
        )
        
        path = obj.attachment_path("test_file.pdf")
        self.assertIn(f"company_{self.basic_form.id}/sswg/", path)
        self.assertIn("test_file", path)

    def test_string_representation(self):
        obj = SmrcNoObjectionData.objects.create(
            basic_form=self.basic_form,
            smrc_no_objection_file=self.test_file,
            created_by=self.user,
            updated_by=self.user
        )
        self.assertEqual(str(obj), str(obj.id))

    def test_verbose_names(self):
        self.assertEqual(
            SmrcNoObjectionData._meta.verbose_name,
            _("SSWG SmrcNoObjectionData")
        )
        self.assertEqual(
            SmrcNoObjectionData._meta.verbose_name_plural,
            _("SSWG SmrcNoObjectionData")
        )
class MmAceptanceDataTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.basic_form = BasicForm.objects.create(
            date=timezone.now().date(),
            sn_no="TEST-002",
            created_by=self.user,
            updated_by=self.user
        )
        
        self.test_file = SimpleUploadedFile(
            "mm_acceptance.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_mm_acceptance_creation(self):
        obj = MmAceptanceData.objects.create(
            basic_form=self.basic_form,
            mm_aceptance_file=self.test_file,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(obj.basic_form.sn_no, "TEST-002")
        self.assertIn("mm_acceptance", obj.mm_aceptance_file.name)
        self.assertTrue(obj.created_at)

    def test_verbose_names(self):
        self.assertEqual(
            MmAceptanceData._meta.verbose_name,
            _("SSWG MmAceptanceData")
        )
        self.assertEqual(
            MmAceptanceData._meta.verbose_name_plural,
            _("SSWG MmAceptanceData")
        )

class MOCSDataTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.basic_form = BasicForm.objects.create(
            date=timezone.now().date(),
            sn_no="TEST-003",
            created_by=self.user,
            updated_by=self.user
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
            mocs2_file=self.test_file2,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(obj.contract_number, "CON-123")
        self.assertEqual(obj.unit_price_in_grams, 50.0)
        self.assertIn("mocs1", obj.mocs1_file.name)
        self.assertIn("mocs2", obj.mocs2_file.name)

class CBSDataTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )

        self.basic_form = BasicForm.objects.create(
            date=timezone.now().date(),
            sn_no="TEST-004",
            created_by=self.user,
            updated_by=self.user
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
            cbs_file=self.test_file,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(obj.customer_account_number, "ACC-789")
        self.assertEqual(obj.payment_method, "transfer")
        self.assertIn("cbs_report", obj.cbs_file.name)
        self.assertEqual(str(obj), f"CBS-{obj.customer_account_number}")
