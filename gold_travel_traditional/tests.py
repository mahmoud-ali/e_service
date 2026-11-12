import io

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.base import BaseStorage
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from company_profile.models import LkpState
from gold_travel_traditional.admin.melt_produce import MeltProduceAdmin
from gold_travel_traditional.forms import MeltProduceForm
from gold_travel_traditional.models import (
    AppMoveGoldTraditional,
    AppMoveGoldTraditionalDetail,
    GoldTravelTraditionalUser,
    GoldTravelTraditionalUserJihatAlaisdar,
    GoldTravelTraditionalUserJihatTarhil,
    LkpJihatAlaisdar,
    LkpJihatAltarhil,
    MeltProduce,
    MeltProduceDetail,
)

UserModel = get_user_model()


def _image_bytes():
    img = Image.new('RGB', (20, 20), color=(200, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()


def _image_file(name='test.jpg'):
    return ContentFile(_image_bytes(), name=name)


class MeltProduceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.state = LkpState.objects.create(name="Khartoum", code="KRT", x=1.0, y=1.0)
        cls.jihat_alaisdar = LkpJihatAlaisdar.objects.create(state=cls.state, name="Issuing point")
        cls.wijhat_altarhil = LkpJihatAltarhil.objects.create(state=cls.state, name="Destination point")

        cls.user1 = UserModel.objects.create_user(username="issuer", password="pass", email="issuer@example.com")
        cls.user2 = UserModel.objects.create_user(username="tarhil", password="pass", email="tarhil@example.com")
        cls.user3 = UserModel.objects.create_user(username="both", password="pass", email="both@example.com")
        cls.user4 = UserModel.objects.create_user(username="manager", password="pass", email="manager@example.com")
        cls.user5 = UserModel.objects.create_user(username="viewer", password="pass", email="viewer@example.com")

        cls.gold_user1 = GoldTravelTraditionalUser.objects.create(
            user=cls.user1, name="Issuer", state=cls.state,
            user_type=GoldTravelTraditionalUser.JIHAT_ALAISDAR,
            created_by=cls.user1, updated_by=cls.user1,
        )
        cls.gold_user2 = GoldTravelTraditionalUser.objects.create(
            user=cls.user2, name="Tarhil", state=cls.state,
            user_type=GoldTravelTraditionalUser.JIHAT_TARHIL,
            created_by=cls.user2, updated_by=cls.user2,
        )
        cls.gold_user3 = GoldTravelTraditionalUser.objects.create(
            user=cls.user3, name="Both", state=cls.state,
            user_type=GoldTravelTraditionalUser.BOTH,
            created_by=cls.user3, updated_by=cls.user3,
        )
        cls.gold_user4 = GoldTravelTraditionalUser.objects.create(
            user=cls.user4, name="Manager", state=cls.state,
            user_type=GoldTravelTraditionalUser.STATE_MANAGER,
            created_by=cls.user4, updated_by=cls.user4,
        )
        cls.gold_user5 = GoldTravelTraditionalUser.objects.create(
            user=cls.user5, name="Viewer", state=cls.state,
            user_type=GoldTravelTraditionalUser.STATE_VIEWER,
            created_by=cls.user5, updated_by=cls.user5,
        )

        GoldTravelTraditionalUserJihatAlaisdar.objects.create(
            master=cls.gold_user1, jihat_alaisdar=cls.jihat_alaisdar,
        )
        GoldTravelTraditionalUserJihatTarhil.objects.create(
            master=cls.gold_user1, wijhat_altarhil=cls.wijhat_altarhil, can_arrive=False,
        )

    def _create_melt(self, details=None):
        melt = MeltProduce.objects.create(
            issue_date=timezone.now().date(),
            almustafid_name="أحمد محمد",
            almustafid_phone="0912345678",
            almustafid_identity_type=AppMoveGoldTraditional.IDENTITY_NATIONAL_ID,
            almustafid_identity="12345678901",
            almustafid_identity_attachement=_image_file(),
            melt_workshop="ورشة صهر",
            source_state=self.state,
            created_by=self.user1,
            updated_by=self.user1,
        )
        for weight, shape in (details or []):
            MeltProduceDetail.objects.create(master=melt, alloy_weight_gram=weight, alloy_shape=shape)
        return melt

    def test_code_generation(self):
        melt = self._create_melt()
        self.assertTrue(melt.code.startswith("MP-KRT-"))
        self.assertEqual(len(melt.code), len("MP-KRT-YYYYMM-0001"))

    def test_produced_record_property(self):
        melt = self._create_melt(details=[(10.0, MeltProduceDetail.SHAPE_CIRCULAR)])
        permit = AppMoveGoldTraditional.objects.create(
            issue_date=melt.issue_date,
            almustafid_name=melt.almustafid_name,
            almustafid_phone=melt.almustafid_phone,
            almustafid_identity_type=melt.almustafid_identity_type,
            almustafid_identity=melt.almustafid_identity,
            almustafid_identity_attachement=_image_file(),
            jihat_alaisdar=self.jihat_alaisdar,
            wijhat_altarhil=self.wijhat_altarhil,
            attachement_file=_image_file(),
            source_state=self.state,
            melt_produce=melt,
            created_by=self.user1,
            updated_by=self.user1,
        )
        self.assertEqual(melt.produced_record, permit)

    def test_soug_name_from_user_data(self):
        melt = self._create_melt()
        self.assertEqual(melt.soug_name, self.jihat_alaisdar.name)

    def test_soug_name_empty_when_no_assignment(self):
        melt = self._create_melt()
        melt.created_by = self.user3
        melt.save(update_fields=['created_by'])
        self.assertEqual(melt.soug_name, '')

    def test_clean_blocks_edit_when_complete(self):
        melt = self._create_melt(details=[(10.0, MeltProduceDetail.SHAPE_CIRCULAR)])
        melt.state = MeltProduce.STATE_COMPLETE
        melt.save()
        melt.melt_workshop = "ورشة أخرى"
        with self.assertRaises(ValidationError):
            melt.clean()

    def test_clean_requires_details_to_complete(self):
        melt = self._create_melt()
        melt.state = MeltProduce.STATE_COMPLETE
        with self.assertRaises(ValidationError):
            melt.clean()

    def test_form_requires_11_digit_identity(self):
        form = MeltProduceForm(data={
            'issue_date': timezone.now().date(),
            'almustafid_name': 'أحمد',
            'almustafid_phone': '0912345678',
            'almustafid_identity_type': AppMoveGoldTraditional.IDENTITY_NATIONAL_ID,
            'almustafid_identity': '12345',
            'melt_workshop': 'ورشة',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('almustafid_identity', form.errors)

    def test_has_add_permission(self):
        model_admin = MeltProduceAdmin(MeltProduce, admin.site)
        factory = RequestFactory()

        req = factory.get('/')
        req.user = self.user1
        self.assertTrue(model_admin.has_add_permission(req))

        req.user = self.user3
        self.assertTrue(model_admin.has_add_permission(req))

        for user in (self.user2, self.user4, self.user5):
            req.user = user
            self.assertFalse(model_admin.has_add_permission(req))

    def test_produce_view_creates_permit_and_completes(self):
        melt = self._create_melt(details=[
            (10.0, MeltProduceDetail.SHAPE_CIRCULAR),
            (20.0, MeltProduceDetail.SHAPE_RECTANGULAR),
        ])

        model_admin = MeltProduceAdmin(MeltProduce, admin.site)
        factory = RequestFactory()
        url = reverse("admin:gold_travel_traditional_meltproduce_produce", args=[melt.pk])
        req = factory.post(url, data={
            'jihat_alaisdar': self.jihat_alaisdar.pk,
            'wijhat_altarhil': self.wijhat_altarhil.pk,
        })
        req.user = self.user1
        req._messages = BaseStorage(req)
        req.FILES['attachement_file'] = SimpleUploadedFile('gold.jpg', _image_bytes(), content_type='image/jpeg')

        response = model_admin.produce_view(req, melt.pk)

        melt.refresh_from_db()
        self.assertEqual(melt.state, MeltProduce.STATE_COMPLETE)

        permit = melt.produced_record
        self.assertIsNotNone(permit)
        self.assertEqual(permit.details.count(), 2)
        self.assertEqual(permit.almustafid_name, melt.almustafid_name)
        self.assertEqual(permit.almustafid_phone, melt.almustafid_phone)
        self.assertEqual(permit.almustafid_identity, melt.almustafid_identity)
        self.assertEqual(permit.melt_workshop, melt.melt_workshop)
        self.assertEqual(permit.melt_produce_id, melt.pk)
        self.assertEqual(
            list(permit.details.values_list('alloy_weight_gram', flat=True)),
            [10.0, 20.0],
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(str(permit.pk), response.url)
