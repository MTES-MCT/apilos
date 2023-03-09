from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.core import mail
from django.core.files.storage import default_storage

from bailleurs.models import SousNatureBailleur
from conventions.models.convention import Convention
from conventions.tasks import generate_and_send
from core.services import EmailTemplateID
from programmes.models import NatureLogement


@override_settings(EMAIL_BACKEND="anymail.backends.test.EmailBackend")
@override_settings(SENDINBLUE_API_KEY="fake_sendinblue_api_key")
class GenerateAndSendTest(TestCase):
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

    @classmethod
    def setUpTestData(cls):
        with (Path(__file__).parent / "fixtures" / "convention.pdf").open("r") as f:
            default_storage.save("convention.pdf", f)

    def setUp(self):
        self.convention = (
            Convention.objects.prefetch_related("programme__bailleur")
            .prefetch_related("programme__administration")
            .order_by("uuid")
            .first()
        )
        self.convention.programme.bailleur.sous_nature_bailleur = (
            SousNatureBailleur.SEM_EPL
        )
        self.convention.programme.bailleur.save()
        self.convention.programme.administration.adresse = "1 rue de la paix"
        self.convention.programme.administration.code_postal = "75000"
        self.convention.programme.administration.ville = "Paris"
        self.convention.programme.administration.nb_convention_exemplaires = 12
        self.convention.programme.administration.save()

    def test_generate_and_send_logement_ordinaire(self):
        self.convention.programme.nature_logement = NatureLogement.LOGEMENTSORDINAIRES
        self.convention.programme.save()
        args = {
            "convention_uuid": str(self.convention.uuid),
            "convention_url": "https://target.to.convention.display",
            "convention_email_validator": "validator@apilos.fr",
        }

        with patch("conventions.tasks.generate_convention_doc", autospec=True):
            with patch(
                "conventions.tasks.generate_pdf", autospec=True
            ) as mocked_generate_pdf:
                mocked_generate_pdf.return_value = "convention.pdf"
                args = {
                    "convention_uuid": str(self.convention.uuid),
                    "convention_url": "https://target.to.convention.display",
                    "convention_email_validator": "validator@apilos.fr",
                }
                generate_and_send(args)
                self.assertEqual(
                    mail.outbox[0].anymail_test_params["attachments"][0].name,
                    "convention.pdf",
                )
                self.assertEqual(
                    mail.outbox[0].anymail_test_params["template_id"],
                    EmailTemplateID.ItoB_CONVENTION_VALIDEE.value,
                )
                self.assertDictEqual(
                    mail.outbox[0].anymail_test_params["merge_global_data"],
                    {
                        "convention_url": "https://target.to.convention.display",
                        "convention": str(self.convention),
                        "adresse": "1 rue de la paix",
                        "code_postal": "75000",
                        "ville": "Paris",
                        "nb_convention_exemplaires": 12,
                    },
                )
                self.convention.programme.nature_logement = (
                    NatureLogement.RESIDENCEUNIVERSITAIRE
                )
                self.convention.programme.save()
                generate_and_send(args)
                self.assertEqual(
                    mail.outbox[0].anymail_test_params["attachments"][0].name,
                    "convention.pdf",
                )
                self.assertEqual(
                    mail.outbox[0].anymail_test_params["template_id"],
                    EmailTemplateID.ItoB_CONVENTION_VALIDEE.value,
                )
                self.assertDictEqual(
                    mail.outbox[0].anymail_test_params["merge_global_data"],
                    {
                        "convention_url": "https://target.to.convention.display",
                        "convention": str(self.convention),
                        "adresse": "1 rue de la paix",
                        "code_postal": "75000",
                        "ville": "Paris",
                        "nb_convention_exemplaires": 12,
                    },
                )

    def test_generate_and_send_foyer(self):
        self.convention.programme.nature_logement = NatureLogement.AUTRE
        self.convention.programme.save()
        args = {
            "convention_uuid": str(self.convention.uuid),
            "convention_url": "https://target.to.convention.display",
            "convention_email_validator": "validator@apilos.fr",
        }

        with patch("conventions.tasks.generate_convention_doc", autospec=True):
            with patch(
                "conventions.tasks.generate_pdf", autospec=True
            ) as mocked_generate_pdf:
                mocked_generate_pdf.return_value = "convention.pdf"
                generate_and_send(args)
                self.assertEqual(
                    mail.outbox[0].anymail_test_params["attachments"][0].name,
                    f"convention_{self.convention.uuid}.zip",
                )
                self.assertEqual(
                    mail.outbox[0].anymail_test_params["template_id"],
                    EmailTemplateID.ItoB_CONVENTION_VALIDEE.value,
                )
                self.assertDictEqual(
                    mail.outbox[0].anymail_test_params["merge_global_data"],
                    {
                        "convention_url": "https://target.to.convention.display",
                        "convention": str(self.convention),
                        "adresse": "1 rue de la paix",
                        "code_postal": "75000",
                        "ville": "Paris",
                        "nb_convention_exemplaires": 12,
                    },
                )

    def test_generate_and_send_residence(self):
        self.convention.programme.nature_logement = NatureLogement.RESIDENCEDACCUEIL
        self.convention.programme.save()
        args = {
            "convention_uuid": str(self.convention.uuid),
            "convention_url": "https://target.to.convention.display",
            "convention_email_validator": "validator@apilos.fr",
        }

        with patch("conventions.tasks.generate_convention_doc", autospec=True):
            with patch(
                "conventions.tasks.generate_pdf", autospec=True
            ) as mocked_generate_pdf:
                mocked_generate_pdf.return_value = "convention.pdf"
                generate_and_send(args)
                self.assertEqual(
                    mail.outbox[0].anymail_test_params["attachments"][0].name,
                    f"convention_{self.convention.uuid}.zip",
                )
                self.assertEqual(
                    mail.outbox[0].anymail_test_params["template_id"],
                    EmailTemplateID.ItoB_CONVENTION_VALIDEE.value,
                )
                self.assertDictEqual(
                    mail.outbox[0].anymail_test_params["merge_global_data"],
                    {
                        "convention_url": "https://target.to.convention.display",
                        "convention": str(self.convention),
                        "adresse": "1 rue de la paix",
                        "code_postal": "75000",
                        "ville": "Paris",
                        "nb_convention_exemplaires": 12,
                    },
                )

    def test_generate_and_send_avenant(self):
        self.convention.programme.nature_logement = NatureLogement.RESIDENCEDACCUEIL
        self.convention.programme.save()

        avenant = self.convention.clone(None, convention_origin=self.convention)
        args = {
            "convention_uuid": str(avenant.uuid),
            "convention_url": "https://target.to.convention.display",
            "convention_email_validator": "validator@apilos.fr",
        }
        with patch("conventions.tasks.generate_convention_doc", autospec=True):
            with patch(
                "conventions.tasks.generate_pdf", autospec=True
            ) as mocked_generate_pdf:
                mocked_generate_pdf.return_value = "convention.pdf"
                args = {
                    "convention_uuid": str(avenant.uuid),
                    "convention_url": "https://target.to.convention.display",
                    "convention_email_validator": "validator@apilos.fr",
                }
                generate_and_send(args)
                self.assertEqual(
                    mail.outbox[0].anymail_test_params["attachments"][0].name,
                    "convention.pdf",
                )
                self.assertEqual(
                    mail.outbox[0].anymail_test_params["template_id"],
                    EmailTemplateID.ItoB_AVENANT_VALIDE.value,
                )
                self.assertDictEqual(
                    mail.outbox[0].anymail_test_params["merge_global_data"],
                    {
                        "convention_url": "https://target.to.convention.display",
                        "convention": str(avenant),
                        "adresse": "1 rue de la paix",
                        "code_postal": "75000",
                        "ville": "Paris",
                        "nb_convention_exemplaires": 12,
                    },
                )
