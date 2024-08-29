import uuid

import time_machine
from django.test import TestCase
from rest_framework import serializers
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from upload.models import UploadedFileSerializer

from .factories import UploadedFileFactory


class UploadedFileTest(ParametrizedTestCase, TestCase):
    def test_filepath_with_dirpath(self):
        uploaded_file = UploadedFileFactory(
            filename="image.png",
            dirpath="/path/to/file",
        )
        self.assertEqual(
            uploaded_file.filepath(uuid.uuid4()),
            f"/path/to/file/{uploaded_file.uuid}_image.png",
        )

    def test_filepath_without_dirpath(self):
        uploaded_file = UploadedFileFactory(
            filename="image.png",
            dirpath=None,
        )
        fake_uuid = uuid.uuid4()
        expected_filepath = (
            f"conventions/{fake_uuid}/media/{uploaded_file.uuid}_image.png"
        )
        self.assertEqual(
            uploaded_file.filepath(fake_uuid),
            expected_filepath,
        )

    def test_object_str(self):
        uploaded_file = UploadedFileFactory(filename="image.png")
        self.assertEqual(str(uploaded_file), "image.png")

    @time_machine.travel("2024-08-29")
    def test_serialize(self):
        uploaded_file = UploadedFileFactory(
            filename="image.png",
            dirpath="/path/to/file",
            content_type="image/png",
            size=12345,
        )

        expected_object = {
            "id": uploaded_file.id,
            "uuid": str(uploaded_file.uuid),
            "filename": "image.png",
            "realname": "image.png",
            "dirpath": "/path/to/file",
            "size": "12345",
            "content_type": "image/png",
            "cree_le": "2024-08-29T00:00:00+02:00",
            "mis_a_jour_le": serializers.DateTimeField().to_representation(
                uploaded_file.mis_a_jour_le
            ),
        }

        self.assertEqual(UploadedFileSerializer(uploaded_file).data, expected_object)

    def test_filename_mandatory(self):
        with self.assertRaises(ValueError):
            UploadedFileFactory(filename=None, realname=None)

    @parametrize(
        "filename, realname, expected_filename, expected_realname",
        [
            param(
                "image.png",
                None,
                "image.png",
                "image.png",
                id="null_realname",
            ),
            param(
                None,
                "image.png",
                "image.png",
                "image.png",
                id="null_filename",
            ),
            param(
                "doc 10%.pdf",
                None,
                "doc-10.pdf",
                "doc 10%.pdf",
                id="percent_char",
            ),
            param(
                "doc  hello.you_buddy.pdf",
                None,
                "doc-helloyou_buddy.pdf",
                "doc  hello.you_buddy.pdf",
                id="dot_char_and_more",
            ),
        ],
    )
    def test_compute_filename(
        self, filename, realname, expected_filename, expected_realname
    ):
        uploaded_file = UploadedFileFactory(filename=filename, realname=realname)
        assert uploaded_file.filename == expected_filename
        assert uploaded_file.realname == expected_realname

    def test_filename_updated(self):
        uploaded_file = UploadedFileFactory(filename="image 10%.png")
        assert uploaded_file.filename == "image-10.png"
        assert uploaded_file.realname == "image 10%.png"

        uploaded_file.filename = "new_image.png"
        uploaded_file.save()
        assert uploaded_file.filename == "new_image.png", "filename should change"
        assert uploaded_file.realname == "image 10%.png", "realname should not change"

        uploaded_file.realname = "new_image_2.png"
        uploaded_file.save()
        assert uploaded_file.filename == "new_image.png", "filename should not change"
        assert uploaded_file.realname == "new_image_2.png", "realname should change"
