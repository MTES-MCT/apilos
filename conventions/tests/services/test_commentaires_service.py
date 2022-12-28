import json

from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import (
    ConventionCommentForm,
)
from conventions.models import Convention
from conventions.services import (
    commentaires,
    utils,
)
from core.tests import utils_fixtures
from users.models import User


class ConventionCommentsServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        request.user = User.objects.get(username="fix")
        self.convention_comments_service = commentaires.ConventionCommentsService(
            convention=convention, request=request
        )

    def test_get(self):
        self.convention_comments_service.get()
        self.assertEqual(
            self.convention_comments_service.return_status, utils.ReturnStatus.ERROR
        )
        self.assertIsInstance(
            self.convention_comments_service.form, ConventionCommentForm
        )
        self.assertEqual(
            self.convention_comments_service.form.initial["uuid"],
            self.convention_comments_service.convention.uuid,
        )
        comments = json.loads(self.convention_comments_service.convention.comments)
        text = comments["text"] if "text" in comments else None
        self.assertEqual(
            self.convention_comments_service.form.initial["comments"], text
        )
        files = comments["files"] if "files" in comments else None
        self.assertEqual(
            json.loads(self.convention_comments_service.form.initial["comments_files"]),
            files,
        )

    def test_save(self):
        self.convention_comments_service.request.POST["comments"] = ("E" * 5001,)
        self.convention_comments_service.save()
        self.assertEqual(
            self.convention_comments_service.return_status, utils.ReturnStatus.ERROR
        )
        self.assertTrue(self.convention_comments_service.form.has_error("comments"))

        self.convention_comments_service.request.POST = {
            "comments": "this is a new comment",
            "comments_files": (
                '{"bbfc7e3a-e0e7-4899-a1e1-fc632c3ea6b0": {"uuid": "bbfc7e3a-e0e7'
                + '-4899-a1e1-fc632c3ea6b0", "thumbnail": "data:image/png;base64,'
                + 'BLAH...BLAH...==", "size": 31185, "filename": "acquereur1.png"'
                + '}, "9e69e766-0167-4638-b1ce-f8f0b033e03a": {"uuid": "9e69e766-'
                + '0167-4638-b1ce-f8f0b033e03a", "thumbnail": "data:image/png;bas'
                + 'e64,BLAH...BLAH...==", "size": 69076, "filename": "acquereur2.'
                + 'png"}}'
            ),
        }

        self.convention_comments_service.save()
        self.convention_comments_service.convention.refresh_from_db()
        comments = json.loads(self.convention_comments_service.convention.comments)
        self.assertEqual(
            self.convention_comments_service.return_status, utils.ReturnStatus.SUCCESS
        )
        self.assertEqual(comments["text"], "this is a new comment")
        self.assertEqual(
            comments["files"],
            {
                "bbfc7e3a-e0e7-4899-a1e1-fc632c3ea6b0": {
                    "uuid": "bbfc7e3a-e0e7-4899-a1e1-fc632c3ea6b0",
                    "thumbnail": "data:image/png;base64,BLAH...BLAH...==",
                    "size": 31185,
                    "filename": "acquereur1.png",
                },
                "9e69e766-0167-4638-b1ce-f8f0b033e03a": {
                    "uuid": "9e69e766-0167-4638-b1ce-f8f0b033e03a",
                    "thumbnail": "data:image/png;base64,BLAH...BLAH...==",
                    "size": 69076,
                    "filename": "acquereur2.png",
                },
            },
        )
