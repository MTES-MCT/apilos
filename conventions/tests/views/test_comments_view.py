from django.test import TestCase
from django.urls import reverse
from conventions.models import Convention

from conventions.tests.views.abstract import AbstractEditViewTestCase
from users.models import User


class ConventionCommentairesViewTests(AbstractEditViewTestCase, TestCase):
    fixtures = [
        "auth.json",
        # "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self):
        super().setUp()
        self.target_path = reverse(
            "conventions:commentaires", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/commentaires.html"
        self.error_payload = {"commentaires": "O" * 5001}
        self.success_payload = {"commentaires": "This is a comment"}
        self.msg_prefix = "[ConventionCommentairesViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertEqual(
            self.convention_75.commentaires,
            '{"files": [], "text": "This is a comment"}',
            msg=f"{self.msg_prefix}",
        )


class AvenantCommentsViewTests(ConventionCommentairesViewTests):
    def setUp(self):
        super().setUp()
        # force convention_75 to be an avenant
        user = User.objects.get(username="fix")
        convention = Convention.objects.get(numero="0001")
        self.convention_75 = convention.clone(user, convention_origin=convention)
        self.target_path = reverse(
            "conventions:avenant_commentaires", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )
        self.msg_prefix = "[AvenantCommentsViewTests] "
