import tempfile
from pathlib import Path

import responses
from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from waffle.testutils import override_switch

from conventions.models.convention import Convention
from core.services import EmailTemplateID
from upload.models import UploadedFile
from upload.tasks import get_clamav_auth_header, scan_uploaded_files
from users.models import User


class SampleOutput:
    stdout = ""

    def __init__(self, stdout):
        self.stdout = stdout


@override_settings(EMAIL_BACKEND="anymail.backends.test.EmailBackend")
@override_settings(SENDINBLUE_API_KEY="fake_sendinblue_api_key")
@override_settings(CLAMAV_SERVICE_URL="https://clamav.beta.gouv.fr")
class VirusDetection(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "very_dangerous_user", "hackerman@wanadoo.fr", "p@ssw0rd"
        )
        self.user.first_name = "Mr"
        self.user.last_name = "Hacker"
        self.user.save()
        self.sample_file = UploadedFile()
        self.sample_file.save()
        self.clamav_auth_headers = get_clamav_auth_header(
            settings.CLAMAV_SERVICE_USER, settings.CLAMAV_SERVICE_PASSWORD
        )
        self.convention = Convention.objects.first()

    @responses.activate
    @override_switch(settings.SWITCH_SIAP_ALERTS_ON, active=False)
    @override_switch(settings.SWITCH_TRANSACTIONAL_EMAILS_OFF, active=False)
    def test_clamav_malicious_file(self):
        self.client.login(username="very_dangerous_user", password="p@ssw0rd")

        with tempfile.NamedTemporaryFile(dir="media", delete=False) as virus:
            responses.post(
                f"{settings.CLAMAV_SERVICE_URL}/v2/scan",
                json={"malware": False},
            )

            scan_uploaded_files(
                self.convention, [(virus.name, self.sample_file.pk)], self.user.id
            )
            self.assertEqual(len(mail.outbox), 0)

            responses.post(
                f"{settings.CLAMAV_SERVICE_URL}/v2/scan",
                json={"malware": True},
            )
            scan_uploaded_files(
                self.convention, [(virus.name, self.sample_file.pk)], self.user.id
            )
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(
                mail.outbox[0].anymail_test_params["template_id"],
                EmailTemplateID.VIRUS_WARNING.value,
            )
            self.assertDictEqual(
                mail.outbox[0].anymail_test_params["merge_global_data"],
                {
                    "firstname": self.user.first_name,
                    "lastname": self.user.last_name,
                    "filename": Path(virus.name).name,
                },
            )
            self.assertEqual(UploadedFile.objects.all().count(), 0)
            with self.assertRaises(FileNotFoundError):
                scan_uploaded_files(
                    self.convention, [(virus.name, self.sample_file)], self.user.id
                )
