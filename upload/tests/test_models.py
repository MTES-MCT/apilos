import uuid

from django.test import TestCase
from rest_framework import serializers

from upload.models import UploadedFile, UploadedFileSerializer


class UploadedFileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        UploadedFile.objects.create(
            filename="image.png",
            dirpath="/path/to/file",
            size=12345,
            content_type="image/png",
        )

    # create unittest for filepath method
    def test_filepath_with_dirpath(self):
        fake_uuid = uuid.uuid4()
        uploaded_file = UploadedFile.objects.create(
            filename="image.png",
            dirpath="/path/to/file",
            size=12345,
            content_type="image/png",
        )

        expected_filepath = (
            f"{uploaded_file.dirpath}/{uploaded_file.uuid}_{uploaded_file.filename}"
        )
        self.assertEqual(uploaded_file.filepath(fake_uuid), expected_filepath)

    def test_filepath_without_dirpath(self):
        uploaded_file = UploadedFile.objects.create(
            filename="image.png",
            dirpath=None,
            size=12345,
            content_type="image/png",
        )
        fake_uuid = uuid.uuid4()

        expected_filepath = (
            f"conventions/{fake_uuid}/media/"
            f"{uploaded_file.uuid}_{uploaded_file.filename}"
        )
        self.assertEqual(uploaded_file.filepath(fake_uuid), expected_filepath)

    def test_object_str(self):
        uploaded_file = UploadedFile.objects.first()
        expected_object_name = f"{uploaded_file.filename}"
        self.assertEqual(str(uploaded_file), expected_object_name)

    def test_serialise(self):
        uploaded_file = UploadedFile.objects.first()
        expected_object = {
            "id": uploaded_file.id,
            "uuid": str(uploaded_file.uuid),
            "filename": uploaded_file.filename,
            "dirpath": uploaded_file.dirpath,
            "size": uploaded_file.size,
            "content_type": uploaded_file.content_type,
            "cree_le": serializers.DateTimeField().to_representation(
                uploaded_file.cree_le
            ),
            "mis_a_jour_le": serializers.DateTimeField().to_representation(
                uploaded_file.mis_a_jour_le
            ),
        }
        self.assertEqual(UploadedFileSerializer(uploaded_file).data, expected_object)
