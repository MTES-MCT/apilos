from django.test import TestCase
from django.urls import reverse

from conventions.models import Convention, TypeEvenement


class ConventionJournalTests(TestCase):
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

        self.convention_75 = Convention.objects.filter(numero="0001").first()
        self.target_path = reverse(
            "conventions:journal", args=[self.convention_75.uuid]
        )

    def test_view_journal(self):
        """
        En tant qu'utilisateur "staff" je peux consulter les évènements du
        journal de bord d'une convention
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.get(self.target_path)
        self.assertEqual(self.convention_75.evenements.count(), 1)
        self.assertEqual(response.status_code, 200, msg="[ConventionJournalTests] ")

    def test_create_journal_evenement(self):
        """
        En tant qu'utilisateur "staff" je peux créer un nouvel évènement sur le
        journal de bord d'une convention
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})
        response = self.client.post(
            self.target_path,
            {
                "action": "submit",
                "description": "Signé par le préfet",
                "type_evenement": TypeEvenement.RETOUR_PREFET,
                "piece_jointe": "filename.jpg",
                "piece_jointe_files": "",
            },
        )
        self.assertEqual(response.status_code, 200, msg="[ConventionJournalTests] ")
        self.convention_75.refresh_from_db()
        self.assertEqual(self.convention_75.evenements.count(), 2)

        evenement = self.convention_75.evenements.last()
        self.assertIsNotNone(evenement)
        self.assertEqual(evenement.description, "Signé par le préfet")
        self.assertEqual(evenement.type_evenement, TypeEvenement.RETOUR_PREFET)
        assert evenement.piece_jointe == '{"files": [], "text": "filename.jpg"}'

    def test_edit_journal_evenement(self):
        """
        En tant qu'utilisateur "staff" je peux éditer un évènement sur le
        journal de bord d'une convention
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.post(
            self.target_path,
            {
                "action": "submit",
                "uuid": self.convention_75.evenements.first().uuid,
                "description": "Contact prélimiaire au préfet pour signature",
                "type_evenement": TypeEvenement.ECHANGE,
                "piece_jointe": "filename_update.jpg",
                "piece_jointe_files": "",
            },
        )
        self.assertEqual(response.status_code, 200, msg="[ConventionJournalTests] ")

        self.convention_75.refresh_from_db()
        self.assertEqual(self.convention_75.evenements.count(), 1)

        evenement = self.convention_75.evenements.first()
        self.assertIsNotNone(evenement)
        self.assertEqual(
            evenement.description,
            "Contact prélimiaire au préfet pour signature",
        )
        self.assertEqual(evenement.type_evenement, TypeEvenement.ECHANGE)
        assert evenement.piece_jointe == '{"files": [], "text": "filename_update.jpg"}'
