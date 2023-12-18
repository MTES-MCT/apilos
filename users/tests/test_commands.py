import datetime
from datetime import date
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings


class SendMonthlyEmailsCommandTest(TestCase):
    def _run_command(self, arguments: list | None = None) -> (StringIO, StringIO):
        if arguments is None:
            arguments = []

        out = StringIO()
        err = StringIO()
        call_command("send_monthly_emails", *arguments, stdout=out, stderr=err)

        return out, err

    @override_settings(CRON_ENABLED=True)
    @override_settings(APPLICATION_DOMAIN_URL="http://localhost:8001")
    @mock.patch(
        "users.management.commands.send_monthly_emails.datetime", wraps=datetime
    )
    def test_run_first_monday_of_month(self, mock_datetime):
        """
        Teste de lancer la commande le premier lundi du mois et avec la bonne
        configuration. Les emails doivent partir.
        """
        mock_datetime.date.today.return_value = date(2023, 4, 3)

        out, err = self._run_command()

        self.assertEqual(
            out.getvalue().strip(),
            "0 email(s) instructeur envoyé(s)\n0 email(s) bailleur envoyé(s)",
        )
        self.assertEqual(err.getvalue().strip(), "")

    @override_settings(APPLICATION_DOMAIN_URL="http://localhost:8001")
    def test_run_forced(self):
        """
        Teste de lancer la commande en mode forcé du mois et avec la bonne
        configuration. Les emails doivent partir.
        """
        out, err = self._run_command(["--force"])

        self.assertEqual(
            out.getvalue().strip(),
            "0 email(s) instructeur envoyé(s)\n0 email(s) bailleur envoyé(s)",
        )
        self.assertEqual(err.getvalue().strip(), "")

    @override_settings(APPLICATION_DOMAIN_URL=None)
    def test_run_forced_misconfigured(self):
        """
        Teste de lancer la commande en mode forcé du mois, mais avec une
        configuration incomplète. Une exception doit être jetée et aucun email
        ne doit partir.
        """
        with self.assertRaises(Exception) as e:
            _, _ = self._run_command(["--force"])

        self.assertEqual(
            str(e.exception),
            "La variable APPLICATION_DOMAIN_URL \
doit être définie pour pouvoir envoyer des emails",
        )

    def test_run_default(self):
        """
        Teste de lancer la commande sans la moindre configuration. Aucun email
        ne doit être envoyé puisque les tâches CRON sont désactivées par défaut.
        """
        out, err = self._run_command()

        self.assertEqual(out.getvalue().strip(), "")
        self.assertEqual(
            err.getvalue().strip(),
            "Tâches CRON désactivées, \
abandon",
        )

    @override_settings(CRON_ENABLED=True)
    @override_settings(APPLICATION_DOMAIN_URL=None)
    @mock.patch(
        "users.management.commands.send_monthly_emails.datetime", wraps=datetime
    )
    def test_run_cron_enabled(self, mock_datetime):
        """
        Teste de lancer la commande sans la moindre configuration. Aucun email
        ne doit être envoyé puisque la variable APPLICATION_DOMAIN_URL,
        nécessaire pour les liens dans les emails, n'est pas définie.
        """
        mock_datetime.date.today.return_value = date(2023, 4, 3)

        with self.assertRaises(Exception) as e:
            _, _ = self._run_command()

        self.assertEqual(
            str(e.exception),
            "La variable APPLICATION_DOMAIN_URL \
doit être définie pour pouvoir envoyer des emails",
        )

    @override_settings(CRON_ENABLED=True)
    @override_settings(APPLICATION_DOMAIN_URL="http://localhost:8001")
    @mock.patch(
        "users.management.commands.send_monthly_emails.datetime", wraps=datetime
    )
    def test_run_not_monday(self, mock_datetime):
        """
        Teste de lancer la commande avec la bonne configuration, mais un jour
        autre que lundi. Aucun email ne doit être envoyé.
        """
        mock_datetime.date.today.return_value = date(2023, 4, 11)  # Tuesday

        out, err = self._run_command()

        self.assertEqual(out.getvalue().strip(), "")
        self.assertEqual(
            err.getvalue().strip(),
            "Pas le premier lundi du mois,\
 abandon",
        )

    @override_settings(CRON_ENABLED=True)
    @override_settings(APPLICATION_DOMAIN_URL="http://localhost:8001")
    @mock.patch(
        "users.management.commands.send_monthly_emails.datetime", wraps=datetime
    )
    def test_run_not_first_monday_of_month(self, mock_datetime):
        """
        Teste de lancer la commande avec la bonne configuration, mais un lundi
        qui n'est pas le premier du mois. Aucun email ne doit être envoyé.
        """
        mock_datetime.date.today.return_value = date(2023, 4, 10)

        out, err = self._run_command()

        self.assertEqual(out.getvalue().strip(), "")
        self.assertEqual(
            err.getvalue().strip(),
            "Pas le premier lundi du mois,\
 abandon",
        )
