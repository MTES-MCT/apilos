from django.core.management import call_command
from django.test import TestCase

from conventions.models import Convention
from instructeurs.models import Administration
from programmes.models import Programme
from programmes.tests.factories import DepartementFactory


class ReassignAdministrationTest(TestCase):
    fixtures = [
        "auth.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self):
        self.admin1 = Administration.objects.create(code="3311")
        self.admin2 = Administration.objects.create(code="3312")
        self.admin3 = Administration.objects.create(code="3313")

        DepartementFactory(nom="Lot", code_insee="46")
        DepartementFactory(nom="Aube", code_insee="10")

        self.programme1 = Programme.objects.create(
            administration=self.admin1,
            bailleur_id=1,
            nom="Programme 1",
            code_postal="46000",
            code_insee_departement="46",
        )
        self.programme2 = Programme.objects.create(
            administration=self.admin2,
            bailleur_id=1,
            nom="Programme 2",
            code_postal="10800",
            code_insee_departement="10",
        )

        self.convention1 = Convention.objects.create(
            programme=self.programme1, lot_id=1, numero="991"
        )
        self.convention2 = Convention.objects.create(
            programme=self.programme2, lot_id=2, numero="992"
        )

    def _refresh_from_db(self):
        self.programme1.refresh_from_db()
        self.programme2.refresh_from_db()

        self.convention1.refresh_from_db()
        self.convention2.refresh_from_db()

    def test_reassign_administration_different_programs(self):
        args = []
        kwargs = {
            "departements": ["46"],
            "new_admin_code": str(self.admin3.code),
            "no_dry_run": True,
        }
        call_command("reassign_administration", *args, **kwargs)

        self._refresh_from_db()

        # Ensure admin has changed
        assert self.convention1.administration == self.admin3
        assert (
            self.convention1.programme.reassign_command_old_admin_backup
            == self.admin1.code
        )
        # Departement not in the perimeter: no change
        assert self.convention2.administration == self.admin2
        assert self.convention2.programme.reassign_command_old_admin_backup is None

    def test_reassign_administration_different_programs_dry_run(self):
        args = []
        kwargs = {
            "departements": ["46"],
            "new_admin_code": str(self.admin3.code),
        }
        call_command("reassign_administration", *args, **kwargs)

        self._refresh_from_db()

        # Dry run: no changes
        assert self.convention1.administration == self.admin1
        assert self.convention1.programme.reassign_command_old_admin_backup is None
        assert self.convention2.administration == self.admin2
        assert self.convention1.programme.reassign_command_old_admin_backup is None
