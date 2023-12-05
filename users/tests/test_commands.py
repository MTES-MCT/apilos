import datetime
from datetime import date
from io import StringIO
from unittest import mock

from django.test import override_settings
from django.core.management import call_command
from django.test import TestCase
from users.models import User


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


class UpdateStaffUsersPermsTest(TestCase):
    def _run_command(self):
        out = StringIO()
        err = StringIO()
        call_command("update_staff_users_perms", stdout=out, stderr=err)

    def test_not_added_if_superuser(self):
        admin_user = User.objects.create_user(
            username="admin", password="12345", is_staff=True, is_superuser=True
        )
        assert admin_user.is_staff is True
        assert admin_user.is_superuser is True
        assert admin_user.user_permissions.count() == 0

        self._run_command()

        admin_user.refresh_from_db()
        assert admin_user.user_permissions.count() == 0

    def test_permissions_added(self):
        staff_user = User.objects.create_user(
            username="staff", password="12345", is_staff=True
        )
        assert staff_user.is_staff is True
        assert staff_user.is_superuser is False
        assert staff_user.user_permissions.count() == 0

        self._run_command()

        staff_user.refresh_from_db()
        assert sorted(
            staff_user.user_permissions.values_list("codename", flat=True)
        ) == [
            "add_administration",
            "add_annexe",
            "add_avenanttype",
            "add_bailleur",
            "add_convention",
            "add_departement",
            "add_ecoloreference",
            "add_evenement",
            "add_indiceevolutionloyer",
            "add_locauxcollectifs",
            "add_logement",
            "add_logementedd",
            "add_lot",
            "add_pret",
            "add_programme",
            "add_referencecadastrale",
            "add_repartitionsurface",
            "add_typestationnement",
            "add_user",
            "change_administration",
            "change_annexe",
            "change_avenanttype",
            "change_bailleur",
            "change_convention",
            "change_departement",
            "change_ecoloreference",
            "change_evenement",
            "change_indiceevolutionloyer",
            "change_locauxcollectifs",
            "change_logement",
            "change_logementedd",
            "change_lot",
            "change_pret",
            "change_programme",
            "change_referencecadastrale",
            "change_repartitionsurface",
            "change_typestationnement",
            "change_user",
            "view_administration",
            "view_annexe",
            "view_avenanttype",
            "view_bailleur",
            "view_convention",
            "view_departement",
            "view_ecoloreference",
            "view_evenement",
            "view_indiceevolutionloyer",
            "view_locauxcollectifs",
            "view_logement",
            "view_logementedd",
            "view_lot",
            "view_pret",
            "view_programme",
            "view_referencecadastrale",
            "view_repartitionsurface",
            "view_typestationnement",
            "view_user",
        ]
