from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from company_profile.models import LkpState
from sswg.models import BasicForm, CompanyDetails, TransferRelocationFormData, SSMOData, SmrcNoObjectionData, MOCSData
from gold_travel.models import LkpOwner, AppMoveGold
import datetime

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
