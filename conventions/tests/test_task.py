from pathlib import Path
from unittest.mock import Mock, patch

from django.core import mail
from django.core.files.storage import default_storage
from django.test import TestCase, override_settings

from bailleurs.models import SousNatureBailleur
from conventions.tasks import task_generate_and_send
from conventions.tests.factories import ConventionFactory
from core.services import EmailTemplateID
from instructeurs.tests.factories import AdministrationFactory
from programmes.models import NatureLogement
from programmes.tests.factories import ProgrammeFactory


@override_settings(EMAIL_BACKEND="anymail.backends.test.EmailBackend")
@override_settings(SENDINBLUE_API_KEY="fake_sendinblue_api_key")
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
@patch(
    "conventions.models.convention.Convention.get_email_bailleur_users",
    Mock(return_value=["validator@apilos.fr"]),
)
@patch("conventions.tasks.generate_pdf", autospec=True)
@patch("conventions.tasks.get_or_generate_convention_doc", autospec=True)
class GenerateAndSendTest(TestCase):
    def _create_pdf_file_in_storage(self, convention_uuid: str):
        dst_path = Path(
            "conventions", convention_uuid, "convention_docs", f"{convention_uuid}.pdf"
        )
        with (Path(__file__).parent / "fixtures" / "convention.pdf").open("r") as f:
            default_storage.save(dst_path, f)

    def setUp(self):
        self.programme = ProgrammeFactory(
            bailleur__sous_nature_bailleur=SousNatureBailleur.SEM_EPL,
            administration=AdministrationFactory(
                adresse="1 rue de la paix",
                code_postal="75000",
                ville="Paris",
                nb_convention_exemplaires=12,
            ),
        )
        self.convention = ConventionFactory(programme=self.programme)
        self._create_pdf_file_in_storage(convention_uuid=str(self.convention.uuid))

    def test_generate_and_send_logement_ordinaire(
        self, mock_get_or_generate_convention_doc, mock_generate_pdf
    ):
        self.programme.nature_logement = NatureLogement.LOGEMENTSORDINAIRES
        self.programme.save()

        task_kwargs = {
            "convention_uuid": str(self.convention.uuid),
            "convention_url": "https://target.to.convention.display",
            "convention_email_validator": "validator@apilos.fr",
        }

        task_generate_and_send(**task_kwargs)

        mock_get_or_generate_convention_doc.assert_called_once_with(
            convention=self.convention, save_data=True
        )
        mock_generate_pdf.assert_called_once_with(
            convention_uuid=str(self.convention.uuid),
            doc=mock_get_or_generate_convention_doc.return_value,
        )

        self.assertEqual(
            mail.outbox[0].anymail_test_params["attachments"][0].name,
            f"{str(self.convention.uuid)}.pdf",
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
        task_generate_and_send(**task_kwargs)
        self.assertEqual(
            mail.outbox[0].anymail_test_params["attachments"][0].name,
            f"{self.convention.uuid}.pdf",
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

    def test_generate_and_send_foyer(
        self, mock_get_or_generate_convention_doc, mock_generate_pdf
    ):
        self.programme.nature_logement = NatureLogement.AUTRE
        self.programme.save()

        task_generate_and_send(
            convention_uuid=str(self.convention.uuid),
            convention_url="https://target.to.convention.display",
            convention_email_validator="validator@apilos.fr",
        )

        mock_get_or_generate_convention_doc.assert_called_once_with(
            convention=self.convention, save_data=True
        )
        mock_generate_pdf.assert_called_once_with(
            convention_uuid=str(self.convention.uuid),
            doc=mock_get_or_generate_convention_doc.return_value,
        )

        self.assertEqual(
            mail.outbox[0].anymail_test_params["attachments"][0].name,
            f"{self.convention.uuid}.zip",
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

    def test_generate_and_send_residence(
        self, mock_get_or_generate_convention_doc, mock_generate_pdf
    ):
        self.programme.nature_logement = NatureLogement.RESIDENCEDACCUEIL
        self.programme.save()

        task_generate_and_send(
            convention_uuid=str(self.convention.uuid),
            convention_url="https://target.to.convention.display",
            convention_email_validator="validator@apilos.fr",
        )

        mock_get_or_generate_convention_doc.assert_called_once_with(
            convention=self.convention, save_data=True
        )
        mock_generate_pdf.assert_called_once_with(
            convention_uuid=str(self.convention.uuid),
            doc=mock_get_or_generate_convention_doc.return_value,
        )

        self.assertEqual(
            mail.outbox[0].anymail_test_params["attachments"][0].name,
            f"{self.convention.uuid}.zip",
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

    def test_generate_and_send_avenant(
        self, mock_get_or_generate_convention_doc, mock_generate_pdf
    ):
        self.programme.nature_logement = NatureLogement.RESIDENCEDACCUEIL
        self.programme.save()

        avenant = self.convention.clone(None, convention_origin=self.convention)
        args = {
            "convention_uuid": str(avenant.uuid),
            "convention_url": "https://target.to.convention.display",
            "convention_email_validator": "validator@apilos.fr",
        }
        self._create_pdf_file_in_storage(convention_uuid=str(avenant.uuid))

        task_generate_and_send(**args)

        mock_get_or_generate_convention_doc.assert_called_once_with(
            convention=avenant, save_data=True
        )
        mock_generate_pdf.assert_called_once_with(
            convention_uuid=str(avenant.uuid),
            doc=mock_get_or_generate_convention_doc.return_value,
        )

        self.assertEqual(
            mail.outbox[0].anymail_test_params["attachments"][0].name,
            f"{avenant.uuid}.pdf",
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
