import tempfile
from pathlib import Path
from unittest import mock

from django.core import mail
from django.test import TestCase, override_settings

from core.services import EmailTemplateID
from upload.models import UploadedFile
from upload.tasks import scan_uploaded_files
from users.models import User


class SampleOutput:
    stdout = ""

    def __init__(self, stdout):
        self.stdout = stdout


@override_settings(EMAIL_BACKEND="anymail.backends.test.EmailBackend")
@override_settings(SENDINBLUE_API_KEY="fake_sendinblue_api_key")
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

    @mock.patch("subprocess.run")
    def test_clamav_email_sending(self, mock_subprocess_run):
        self.client.login(username="very_dangerous_user", password="p@ssw0rd")
        mock_subprocess_run.return_value = SampleOutput("Infected files: 0")

        with tempfile.NamedTemporaryFile(dir="media", delete=False) as virus:
            scan_uploaded_files([(virus.name, self.sample_file.pk)], self.user.id)

            self.assertTrue(mock_subprocess_run.called)
            self.assertEqual(len(mail.outbox), 0)

            mock_subprocess_run.return_value = SampleOutput("Infected files: 1")
            scan_uploaded_files([(virus.name, self.sample_file.pk)], self.user.id)
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
                scan_uploaded_files([(virus.name, self.sample_file)], self.user.id)
