from django.test import TestCase

from core.tests import utils_fixtures
from conventions.services import services_conventions
from conventions.services import email as service_email

from conventions.models import Convention
from users.models import User
from users.type_models import EmailPreferences


class ServicesConventionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def test_send_email_instruction(self):
        convention = Convention.objects.get(numero="0001")
        email_sent = services_conventions.send_email_instruction(
            "https://apilos.beta.gouv.fr/my_convention", convention
        )
        self.assertEqual(email_sent[0].to, ["raph@apilos.com"])
        self.assertEqual(email_sent[0].from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(
            email_sent[0].subject, f"Convention à instruire ({convention})"
        )
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent[0].body)
        self.assertEqual(email_sent[1].to, ["sabine@apilos.com"])
        self.assertEqual(email_sent[1].from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(
            email_sent[1].subject, f"Convention à instruire ({convention})"
        )
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent[1].body)

        User.objects.filter(username="raph").update(
            preferences_email=EmailPreferences.AUCUN
        )
        User.objects.filter(username="sabine").update(
            preferences_email=EmailPreferences.AUCUN
        )
        email_sent = services_conventions.send_email_instruction(
            "https://apilos.beta.gouv.fr/my_convention", convention
        )
        self.assertEqual(email_sent[0].to, ["contact@apilos.beta.gouv.fr"])
        self.assertEqual(email_sent[0].from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(
            email_sent[0].subject,
            f"[ATTENTION pas de destinataire à cet email] Convention à instruire ({convention})",
        )
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent[0].body)
        self.assertEqual(email_sent[1].to, ["contact@apilos.beta.gouv.fr"])
        self.assertEqual(email_sent[1].from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(
            email_sent[1].subject,
            f"[ATTENTION pas de destinataire à cet email] Convention à instruire ({convention})",
        )
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent[1].body)

    def test_send_email_validation(self):
        convention = Convention.objects.get(numero="0001")
        email_sent = service_email.send_email_valide(
            "https://apilos.beta.gouv.fr/my_convention", convention, ["me@apilos.com"]
        )
        self.assertEqual(email_sent.to, ["raph@apilos.com"])
        self.assertEqual(email_sent.cc, ["me@apilos.com"])
        self.assertEqual(email_sent.from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(email_sent.subject, f"Convention validé ({convention})")
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent.body)
        self.assertIn(
            "transmettre les exemplaires signés à votre service instructeur.",
            email_sent.body,
        )
        self.assertIn("Imprimer 3 exemplaires en recto verso", email_sent.body)
        self.assertNotIn("1 rue du bois", email_sent.body)
        self.assertNotIn("13001", email_sent.body)
        self.assertNotIn("Marseille", email_sent.body)

        administration = convention.programme.administration
        administration.nb_convention_exemplaires = 1
        administration.adresse = "1 rue du bois"
        administration.code_postal = "13001"
        administration.ville = "Marseilles"
        administration.save()
        email_sent = services_conventions.send_email_valide(
            "https://apilos.beta.gouv.fr/my_convention", convention, ["me@apilos.com"]
        )
        self.assertIn(
            "les exemplaires signés à votre service instructeur à l‘adresse suivante :",
            email_sent.body,
        )
        self.assertIn("Imprimer 1 exemplaire en recto verso", email_sent.body)
        self.assertIn("1 rue du bois", email_sent.body)
        self.assertIn("13001", email_sent.body)
        self.assertIn("Marseille", email_sent.body)

        User.objects.filter(username="raph").update(
            preferences_email=EmailPreferences.AUCUN
        )
        User.objects.filter(username="sabine").update(
            preferences_email=EmailPreferences.AUCUN
        )

        email_sent = service_email.send_email_valide(
            "https://apilos.beta.gouv.fr/my_convention", convention, ["me@apilos.com"]
        )

        self.assertEqual(email_sent.to, ["contact@apilos.beta.gouv.fr"])
        self.assertEqual(email_sent.cc, [])
        self.assertEqual(email_sent.from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(
            email_sent.subject,
            f"[ATTENTION pas de destinataire à cet email] Convention validé ({convention})",
        )
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent.body)

    def test_send_email_correction(self):
        convention = Convention.objects.get(numero="0001")

        email_sent = services_conventions.send_email_correction(
            "https://apilos.beta.gouv.fr/my_convention",
            convention,
            ["me@apilos.com"],
            True,
            "Toto à un vélo",
        )

        self.assertEqual(email_sent.to, ["raph@apilos.com"])
        self.assertEqual(email_sent.cc, ["me@apilos.com"])
        self.assertEqual(email_sent.from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(email_sent.subject, f"Convention à modifier ({convention})")
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent.body)
        self.assertIn("Toto à un vélo", email_sent.body)

        email_sent = services_conventions.send_email_correction(
            "https://apilos.beta.gouv.fr/my_convention", convention, [], False
        )

        self.assertEqual(email_sent.to, ["sabine@apilos.com"])
        self.assertEqual(email_sent.cc, [])
        self.assertEqual(email_sent.from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(email_sent.subject, f"Convention modifiée ({convention})")
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent.body)
        self.assertNotIn("Toto à un vélo", email_sent.body)

        User.objects.filter(username="raph").update(
            preferences_email=EmailPreferences.AUCUN
        )
        User.objects.filter(username="sabine").update(
            preferences_email=EmailPreferences.AUCUN
        )

        email_sent = services_conventions.send_email_correction(
            "https://apilos.beta.gouv.fr/my_convention",
            convention,
            ["me@apilos.com"],
            True,
            "Toto à un vélo",
        )

        self.assertEqual(email_sent.to, ["contact@apilos.beta.gouv.fr"])
        self.assertEqual(email_sent.cc, [])
        self.assertEqual(email_sent.from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(
            email_sent.subject,
            f"[ATTENTION pas de destinataire à cet email] Convention à modifier ({convention})",
        )
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent.body)
        self.assertIn("Toto à un vélo", email_sent.body)

        email_sent = services_conventions.send_email_correction(
            "https://apilos.beta.gouv.fr/my_convention",
            convention,
            [],
            False,
        )

        self.assertEqual(email_sent.to, ["contact@apilos.beta.gouv.fr"])
        self.assertEqual(email_sent.cc, [])
        self.assertEqual(email_sent.from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(
            email_sent.subject,
            f"[ATTENTION pas de destinataire à cet email] Convention modifiée ({convention})",
        )
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent.body)
        self.assertNotIn("Toto à un vélo", email_sent.body)
