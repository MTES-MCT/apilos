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


class ConventionCommentairesServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        request.user = User.objects.get(username="fix")
        self.convention_commentaires_service = (
            commentaires.ConventionCommentairesService(
                convention=convention, request=request
            )
        )

    def test_get(self):
        self.convention_commentaires_service.get()
        self.assertEqual(
            self.convention_commentaires_service.return_status, utils.ReturnStatus.ERROR
        )
        self.assertIsInstance(
            self.convention_commentaires_service.form, ConventionCommentForm
        )
        self.assertEqual(
            self.convention_commentaires_service.form.initial["uuid"],
            self.convention_commentaires_service.convention.uuid,
        )
        commentaires = json.loads(
            self.convention_commentaires_service.convention.commentaires
        )
        text = commentaires["text"] if "text" in commentaires else None
        self.assertEqual(
            self.convention_commentaires_service.form.initial["commentaires"], text
        )
        files = commentaires["files"] if "files" in commentaires else None
        self.assertEqual(
            json.loads(
                self.convention_commentaires_service.form.initial["commentaires_files"]
            ),
            files,
        )

    def test_save(self):
        self.convention_commentaires_service.request.POST["commentaires"] = (
            "E" * 5001,
        )
        self.convention_commentaires_service.save()
        self.assertEqual(
            self.convention_commentaires_service.return_status, utils.ReturnStatus.ERROR
        )
        self.assertTrue(
            self.convention_commentaires_service.form.has_error("commentaires")
        )

        self.convention_commentaires_service.request.POST = {
            "commentaires": "this is a new comment",
            "commentaires_files": (
                '{"bbfc7e3a-e0e7-4899-a1e1-fc632c3ea6b0": {"uuid": "bbfc7e3a-e0e7'
                + '-4899-a1e1-fc632c3ea6b0", "thumbnail": "data:image/png;base64,'
                + 'BLAH...BLAH...==", "size": 31185, "filename": "acquereur1.png"'
                + '}, "9e69e766-0167-4638-b1ce-f8f0b033e03a": {"uuid": "9e69e766-'
                + '0167-4638-b1ce-f8f0b033e03a", "thumbnail": "data:image/png;bas'
                + 'e64,BLAH...BLAH...==", "size": 69076, "filename": "acquereur2.'
                + 'png"}}'
            ),
        }

        self.convention_commentaires_service.save()
        self.convention_commentaires_service.convention.refresh_from_db()
        commentaires = json.loads(
            self.convention_commentaires_service.convention.commentaires
        )
        self.assertEqual(
            self.convention_commentaires_service.return_status,
            utils.ReturnStatus.SUCCESS,
        )
        self.assertEqual(commentaires["text"], "this is a new comment")
        self.assertEqual(
            commentaires["files"],
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
