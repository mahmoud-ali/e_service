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


class ForeignerRecordSecurityTest(EntajSecurityCommentBaseTest):

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

    def test_section_head_transition_fails_without_security_comment(self):
        """section_head يجب ان يفشل في التأكيد اذا لم يضف مسئول الأمن تعليقاً"""
        self.record.security_comment = ""
        target_state = (ForeignerRecord.STATE_CONFIRMED, ForeignerRecord.STATE_CHOICES[ForeignerRecord.STATE_CONFIRMED])
        with self.assertRaises(ValidationError) as ctx:
            self.record.can_transition_to_next_state(self.user_section, target_state)
        self.assertIn("الرجاء كتابة تعليق أفراد الأمن قبل الموافقة", str(ctx.exception))

    def test_security_officer_transition_fails_without_security_comment(self):
        """security_officer يجب ان يفشل في التأكيد اذا لم يكتب تعليقه"""
        self.record.security_comment = ""
        target_state = (ForeignerRecord.STATE_CONFIRMED, ForeignerRecord.STATE_CHOICES[ForeignerRecord.STATE_CONFIRMED])
        with self.assertRaises(ValidationError) as ctx:
            self.record.can_transition_to_next_state(self.user_security, target_state)
        self.assertIn("الرجاء كتابة تعليق أفراد الأمن قبل الموافقة", str(ctx.exception))

    def test_transition_succeeds_with_security_comment(self):
        """يجب ان ينجح الانتقال عند وجود تعليق الأمن"""
        self.record.security_comment = "لا مانع أمنياً"
        target_state = (ForeignerRecord.STATE_CONFIRMED, ForeignerRecord.STATE_CHOICES[ForeignerRecord.STATE_CONFIRMED])
        result = self.record.can_transition_to_next_state(self.user_security, target_state)
        self.assertTrue(result)


class ForeignerProcedureSecurityTest(EntajSecurityCommentBaseTest):

    def setUp(self):
        super().setUp()
        self.proc_type = LkpForeignerProcedureType.objects.create(name="نوع تجريبي")
        self.procedure = ForeignerProcedure.objects.create(
            company_id=self.company.pk,
            procedure_type=self.proc_type,
            procedure_from="2026-01-01",
            procedure_to="2026-12-31",
            procedure_cause="سبب تجريبي",
            state=ForeignerProcedure.STATE_DRAFT,
            created_by=self.user_section,
            updated_by=self.user_section
        )

    def test_transition_fails_without_security_comment(self):
        """يجب ان يفشل الانتقال اذا كان security_comment فارغاً"""
        self.procedure.security_comment = ""
        target_state = (ForeignerProcedure.STATE_CONFIRMED, ForeignerProcedure.STATE_CHOICES[ForeignerProcedure.STATE_CONFIRMED])
        with self.assertRaises(ValidationError) as ctx:
            self.procedure.can_transition_to_next_state(self.user_section, target_state)
        self.assertIn("الرجاء كتابة تعليق أفراد الأمن قبل الموافقة", str(ctx.exception))

    def test_transition_succeeds_with_security_comment(self):
        """يجب ان ينجح الانتقال عند وجود تعليق الأمن"""
        self.procedure.security_comment = "لا مانع أمنياً"
        target_state = (ForeignerProcedure.STATE_CONFIRMED, ForeignerProcedure.STATE_CHOICES[ForeignerProcedure.STATE_CONFIRMED])
        result = self.procedure.can_transition_to_next_state(self.user_security, target_state)
        self.assertTrue(result)
