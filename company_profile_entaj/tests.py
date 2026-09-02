from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import ValidationError

from company_profile_entaj.models import ForeignerRecord, ForeignerPermission, ForeignerProcedure
from company_profile.models import TblCompanyProduction, LkpCompanyProductionStatus, LkpForeignerProcedureType
from company_profile_entaj.models import ForeignerPermissionType

User = get_user_model()


class EntajSecurityCommentBaseTest(TestCase):
    def setUp(self):
        self.section_head_group, _ = Group.objects.get_or_create(name="entaj_section_head")
        self.security_group, _ = Group.objects.get_or_create(name="security_officer")
        self.dept_head_group, _ = Group.objects.get_or_create(name="entaj_department_head")

        self.user_section = User.objects.create_user(username="section_user", password="password")
        self.user_section.groups.add(self.section_head_group)

        self.user_security = User.objects.create_user(username="security_user", password="password")
        self.user_security.groups.add(self.security_group)

        self.status = LkpCompanyProductionStatus.objects.create(name="سارية")
        self.company = TblCompanyProduction.objects.create(
            name_ar="شركة تجريبية",
            name_en="Test Company",
            company_type=TblCompanyProduction.COMPANY_TYPE_ENTAJ,
            status=self.status,
            created_by=self.user_section,
            updated_by=self.user_section
        )


class ForeignerRecordWorkflowTest(EntajSecurityCommentBaseTest):

    def setUp(self):
        super().setUp()
        self.record = ForeignerRecord.objects.create(
            company_id=self.company.pk,
            name="اجنبي تجريبي",
            position="مهندس",
            department="الانتاج",
            salary=5000,
            state=ForeignerRecord.STATE_DRAFT,
            created_by=self.user_section,
            updated_by=self.user_section
        )

    def test_security_officer_has_no_next_states_on_foreigner_record(self):
        """مسئول الأمن يجب ألا يملك أي صلاحية انتقال على سجل الأجنبي"""
        next_states = self.record.get_next_states(self.user_security)
        self.assertEqual(next_states, [])

    def test_section_head_can_confirm_foreigner_record_from_draft(self):
        """رئيس القسم يجب أن يتمكن من تأكيد سجل الأجنبي مباشرة من المسودة"""
        next_states = self.record.get_next_states(self.user_section)
        self.assertIn((ForeignerRecord.STATE_CONFIRMED, ForeignerRecord.STATE_CHOICES[ForeignerRecord.STATE_CONFIRMED]), next_states)
        target_state = (ForeignerRecord.STATE_CONFIRMED, ForeignerRecord.STATE_CHOICES[ForeignerRecord.STATE_CONFIRMED])
        self.assertTrue(self.record.can_transition_to_next_state(self.user_section, target_state))


class ForeignerProcedureWorkflowTest(EntajSecurityCommentBaseTest):

    def setUp(self):
        super().setUp()
        self.proc_type = LkpForeignerProcedureType.objects.create(name="إجراء تجريبي")

        self.procedure = ForeignerProcedure.objects.create(
            company_id=self.company.pk,
            procedure_type=self.proc_type,
            procedure_from="2026-01-01",
            procedure_to="2026-12-31",
            procedure_cause="طلب تجريبي",
            state=ForeignerProcedure.STATE_DRAFT,
            created_by=self.user_section,
            updated_by=self.user_section
        )

    def test_security_officer_has_no_next_states(self):
        """مسئول الأمن لا يملك صلاحية على إجراءات الإنتاج الداخلي"""
        sec_next_states = self.procedure.get_next_states(self.user_security)
        self.assertEqual(sec_next_states, [])

    def test_section_head_can_confirm_from_draft(self):
        """رئيس القسم يؤكد الطلب مباشرة من المسودة"""
        section_next_states = self.procedure.get_next_states(self.user_section)
        self.assertIn((ForeignerProcedure.STATE_CONFIRMED, ForeignerProcedure.STATE_CHOICES[ForeignerProcedure.STATE_CONFIRMED]), section_next_states)

        target_state = (ForeignerProcedure.STATE_CONFIRMED, ForeignerProcedure.STATE_CHOICES[ForeignerProcedure.STATE_CONFIRMED])
        self.assertTrue(self.procedure.can_transition_to_next_state(self.user_section, target_state))

