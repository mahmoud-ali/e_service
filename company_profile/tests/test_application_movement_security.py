from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import ValidationError

from company_profile.models import AppForignerMovement, LkpNationality, TblCompanyProduction, LkpCompanyProductionStatus
from company_profile.workflow import SUBMITTED, ACCEPTED

User = get_user_model()

class AppForignerMovementSecurityTest(TestCase):
    def setUp(self):
        self.accept_group, _ = Group.objects.get_or_create(name="pro_company_application_accept")
        self.security_group, _ = Group.objects.get_or_create(name="security_officer")

        self.user_accept = User.objects.create_user(username="accept_user", password="password")
        self.user_accept.groups.add(self.accept_group)

        self.user_security = User.objects.create_user(username="security_user", password="password")
        self.user_security.groups.add(self.security_group)

        self.status = LkpCompanyProductionStatus.objects.create(name="سارية")
        self.company = TblCompanyProduction.objects.create(
            name_ar="شركة تجريبية",
            name_en="Test Company",
            company_type=TblCompanyProduction.COMPANY_TYPE_ENTAJ,
            status=self.status,
            created_by=self.user_accept,
            updated_by=self.user_accept
        )
        self.nationality = LkpNationality.objects.create(name="سوداني")

        self.app = AppForignerMovement.objects.create(
            company=self.company,
            route_from="Khartoum",
            route_to="Port Sudan",
            period_from="2026-01-01",
            period_to="2026-01-31",
            address_in_sudan="Khartoum",
            nationality=self.nationality,
            passport_no="P123456",
            passport_expiry_date="2028-01-01",
            state=SUBMITTED,
            created_by=self.user_accept,
            updated_by=self.user_accept
        )

    def test_transition_fails_without_security_comment(self):
        """Transitioning to ACCEPTED should fail if security_comment is empty."""
        self.app.recommendation_comments = "توصية بالموافقة"
        self.app.security_comment = ""
        
        with self.assertRaises(ValidationError) as ctx:
            self.app.can_transition_to_next_state(self.user_accept, (ACCEPTED, "Accepted"), obj=self.app)
        
        self.assertIn("لا يمكن إضافة التوصية أو قبول الطلب إلا بعد موافقة وتعليق مسئول الأمن", str(ctx.exception))

    def test_transition_succeeds_with_security_comment_and_recommendation(self):
        """Transitioning to ACCEPTED should succeed if both security_comment and recommendation_comments are set."""
        self.app.security_comment = "لا مانع أمنياً"
        self.app.recommendation_comments = "توصية بالموافقة"
        
        can_proceed = self.app.can_transition_to_next_state(self.user_accept, (ACCEPTED, "Accepted"), obj=self.app)
        self.assertTrue(can_proceed)
