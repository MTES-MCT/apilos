from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from upload.services import UploadService


class TestUploadService(TestCase):
    def setUp(self):
        self.some_convention_dirpath = "some/path"
        self.some_filename = "a_file.pdf"
        self.upload_service = UploadService(
            self.some_convention_dirpath, self.some_filename
        )

    def test_basic(self):
        self.assertEqual(self.upload_service.filename, self.some_filename)
        self.assertEqual(
            self.upload_service.convention_dirpath, self.some_convention_dirpath
        )

    def test_upload_file(self):
        sample_uploaded_file = SimpleUploadedFile(
            self.some_filename, b"file_content", content_type="application/pdf"
        )
        self.upload_service.upload_file(sample_uploaded_file)
        self.assertEqual(
            Path(
                settings.MEDIA_ROOT, self.some_convention_dirpath, self.some_filename
            ).read_text(encoding="utf-8"),
            "file_content",
        )

    def test_upload_file_io(self):
        sample_bytes_io = BytesIO(b"file_content")
        self.upload_service.upload_file_io(sample_bytes_io)
        self.assertEqual(
            Path(
                settings.MEDIA_ROOT, self.some_convention_dirpath, self.some_filename
            ).read_text(encoding="utf-8"),
            "file_content",
        )

    def test_path(self):
        self.assertEqual(self.upload_service.path, "some/path/a_file.pdf")
