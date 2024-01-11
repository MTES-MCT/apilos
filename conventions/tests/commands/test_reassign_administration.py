from datetime import datetime, timezone

from django.core.management import call_command
from django.test import TestCase

from conventions.models import Convention
from instructeurs.models import Administration
from programmes.models import Programme


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

        self.programme1 = Programme.objects.create(
            administration=self.admin1, bailleur_id=1, nom="Programme 1"
        )
        self.programme2 = Programme.objects.create(
            administration=self.admin1, bailleur_id=1, nom="Programme 2"
        )
        self.programme3 = Programme.objects.create(
            administration=self.admin2, bailleur_id=1, nom="Programme 3"
        )

        self.convention1 = Convention.objects.create(
            programme=self.programme1, lot_id=1, numero="991"
        )
        self.convention2 = Convention.objects.create(
            programme=self.programme2, lot_id=2, numero="992"
        )
        self.convention3 = Convention.objects.create(
            programme=self.programme3, lot_id=3, numero="993"
        )
        self.convention2_1 = Convention.objects.create(
            programme=self.programme2, lot_id=1, numero="9921"
        )

        self.convention1.cree_le = datetime(
            year=2019, month=1, day=1, tzinfo=timezone.utc
        )
        self.convention2.cree_le = datetime(
            year=2020, month=12, day=31, tzinfo=timezone.utc
        )
        self.convention3.cree_le = datetime(
            year=2020, month=1, day=1, tzinfo=timezone.utc
        )
        self.convention2_1.cree_le = datetime(
            year=2028, month=2, day=20, tzinfo=timezone.utc
        )
        self.convention1.save()
        self.convention2.save()
        self.convention3.save()

    def _refresh_from_db(self):
        self.programme1.refresh_from_db()
        self.programme2.refresh_from_db()
        self.programme3.refresh_from_db()

        self.convention1.refresh_from_db()
        self.convention2.refresh_from_db()
        self.convention3.refresh_from_db()

    def test_reassign_administration_different_programs(self):
        args = []
        kwargs = {
            "start_date": "2020-01-01",
            "end_date": "2021-12-31",
            "current_admin_code": str(self.admin1.code),
            "new_admin_code": str(self.admin3.code),
            "dry_run": False,
        }
        call_command("reassign_administration", *args, **kwargs)

        self._refresh_from_db()

        # Out of range: no change
        assert self.convention1.administration == self.admin1
        # In range: assigned to new admin
        assert self.convention2.administration == self.admin3
        # In range but assigned to other admin: no change
        assert self.convention3.administration == self.admin2
        # Out of range but using the same program as
        # a convention that has been reassigned: new admin
        assert self.convention2_1.administration == self.admin3

        # Ensure history was saved, with a reason for updates from the command
        all_history = Programme.history.all()
        assert all_history.count() == 4
        programme_2_history = all_history.filter(nom="Programme 2")
        assert programme_2_history.count() == 2
        assert programme_2_history.last().history_change_reason is None
        assert (
            "Reassign administration command"
            in programme_2_history.first().history_change_reason
        )

    def test_reassign_administration_different_programs_dry_run(self):
        args = []
        kwargs = {
            "start_date": "2020-01-01",
            "end_date": "2021-12-31",
            "current_admin_code": str(self.admin1.code),
            "new_admin_code": str(self.admin3.code),
        }
        call_command("reassign_administration", *args, **kwargs)

        self._refresh_from_db()

        # Dry run: no changes
        assert self.convention1.administration == self.admin1
        assert self.convention2.administration == self.admin1
        assert self.convention3.administration == self.admin2
        assert self.convention2_1.administration == self.admin1

        # Ensure we only have creation records in history
        assert Programme.history.all().count() == 3
