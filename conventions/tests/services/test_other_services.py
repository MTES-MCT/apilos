from unittest import mock

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from conventions.models import Convention, ConventionStatut
from conventions.services import utils
from core.services import EmailService, EmailTemplateID
from users.models import GroupProfile


@override_settings(EMAIL_BACKEND="anymail.backends.test.EmailBackend")
class EmailServiceTests(TestCase):
    def test_basic_send_transactional_email(self):
        EmailService(
            to_emails=["bailleur@apilos.fr"],
            email_template_id=EmailTemplateID.BtoI_CONVENTION_A_INSTRUIRE,
        ).send_transactional_email(email_data={"email_param_key": "email_param_value"})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["bailleur@apilos.fr"])
        self.assertEqual(
            mail.outbox[0].anymail_test_params["merge_global_data"]["email_param_key"],
            "email_param_value",
        )

    def test_send_transactional_email_no_emails_valid(self):
        with pytest.raises(Exception, match="recipient for email"):
            EmailService(
                to_emails=["wrong.to.email"],
                email_template_id=EmailTemplateID.BtoI_CONVENTION_A_INSTRUIRE,
            ).send_transactional_email(
                email_data={"email_param_key": "email_param_value"}
            )

    def test_send_transactional_email_filter_wrong_emails(self):
        EmailService(
            to_emails=["to@apilos.fr", "wrong.to.email"],
            cc_emails=["cc@apilos.fr", "wrong.cc.email"],
            email_template_id=EmailTemplateID.BtoI_CONVENTION_A_INSTRUIRE,
        ).send_transactional_email(email_data={"email_param_key": "email_param_value"})
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["to@apilos.fr"]
        assert mail.outbox[0].cc == ["cc@apilos.fr"]

    def test_email_template_id_not_configured(self):
        with self.assertRaises(Exception):  # noqa: B017
            EmailService(to_emails=["bailleur@apilos.fr"]).send_transactional_email()


class ServicesUtilsTests(TestCase):
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

    # set session in request object
    def setUp(self):
        get_response = mock.MagicMock()
        self.request = RequestFactory().get("/conventions")
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_editable_convention(self):
        convention = Convention.objects.get(numero="0001")
        convention.statut = ConventionStatut.PROJET.label
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertTrue(utils.editable_convention(self.request, convention))
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertTrue(utils.editable_convention(self.request, convention))
        self.request.session["currently"] = GroupProfile.STAFF
        self.assertTrue(utils.editable_convention(self.request, convention))

        for statut in [
            ConventionStatut.INSTRUCTION.label,
            ConventionStatut.CORRECTION.label,
        ]:
            convention.statut = statut
            self.request.session["currently"] = GroupProfile.INSTRUCTEUR
            self.assertTrue(utils.editable_convention(self.request, convention))
            self.request.session["currently"] = GroupProfile.BAILLEUR
            self.assertFalse(utils.editable_convention(self.request, convention))
            self.request.session["currently"] = GroupProfile.STAFF
            self.assertTrue(utils.editable_convention(self.request, convention))

        for statut in [ConventionStatut.A_SIGNER.label, ConventionStatut.SIGNEE.label]:
            convention.statut = statut
            self.request.session["currently"] = GroupProfile.INSTRUCTEUR
            self.assertFalse(utils.editable_convention(self.request, convention))
            self.request.session["currently"] = GroupProfile.BAILLEUR
            self.assertFalse(utils.editable_convention(self.request, convention))
            self.request.session["currently"] = GroupProfile.STAFF
            self.assertFalse(utils.editable_convention(self.request, convention))
