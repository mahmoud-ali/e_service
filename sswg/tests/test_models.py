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
