import json

from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.test import RequestFactory, TestCase

from conventions.forms import ConventionCommentForm
from conventions.models import Convention, ConventionStatut
from conventions.services import services_conventions, services_logements, utils
from core.services import EmailService
from core.tests import utils_fixtures
from programmes.forms import TypeStationnementFormSet
from programmes.models import TypeStationnement
from users.models import GroupProfile, User
from users.type_models import EmailPreferences


class ConventionTypeStationnementServiceTests(TestCase):
    service_class = services_logements.ConventionTypeStationnementService

    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        request.user = User.objects.get(username="fix")
        self.service = self.service_class(convention=convention, request=request)

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.formset, TypeStationnementFormSet)

    def test_save(self):
        self.service.request.POST = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-typologie": "GARAGE_AERIEN",
            "form-0-nb_stationnements": 30,
            "form-0-loyer": "",
            "form-1-uuid": "",
            "form-1-typologie": "GARAGE_ENTERRE",
            "form-1-nb_stationnements": "",
            "form-1-loyer": 100.00,
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        for form in self.service.formset.forms:
            self.assertTrue(
                form.has_error("loyer") or form.has_error("nb_stationnements")
            )

        self.service.request.POST = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-typologie": "GARAGE_AERIEN",
            "form-0-nb_stationnements": 30,
            "form-0-loyer": 12,
            "form-1-uuid": "",
            "form-1-typologie": "GARAGE_ENTERRE",
            "form-1-nb_stationnements": 5,
            "form-1-loyer": 10.00,
        }

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
        garage_aerien = TypeStationnement.objects.get(
            lot=self.service.convention.lot, typologie="GARAGE_AERIEN"
        )
        self.assertEqual(garage_aerien.nb_stationnements, 30)
        self.assertEqual(garage_aerien.loyer, 12)
        garage_enterre = TypeStationnement.objects.get(
            lot=self.service.convention.lot, typologie="GARAGE_ENTERRE"
        )
        self.assertEqual(garage_enterre.nb_stationnements, 5)
        self.assertEqual(garage_enterre.loyer, 10)


class ConventionCommentsServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        request.user = User.objects.get(username="fix")
        self.convention_comments_service = (
            services_conventions.ConventionCommentsService(
                convention=convention, request=request
            )
        )

    def test_get_comments(self):
        self.convention_comments_service.get_comments()
        self.assertEqual(
            self.convention_comments_service.return_status, utils.ReturnStatus.ERROR
        )
        self.assertIsInstance(
            self.convention_comments_service.form, ConventionCommentForm
        )
        self.assertEqual(
            self.convention_comments_service.form.initial["uuid"],
            self.convention_comments_service.convention.uuid,
        )
        comments = json.loads(self.convention_comments_service.convention.comments)
        text = comments["text"] if "text" in comments else None
        self.assertEqual(
            self.convention_comments_service.form.initial["comments"], text
        )
        files = comments["files"] if "files" in comments else None
        self.assertEqual(
            json.loads(self.convention_comments_service.form.initial["comments_files"]),
            files,
        )

    def test_save_comments(self):
        self.convention_comments_service.request.POST["comments"] = ("E" * 5001,)
        self.convention_comments_service.save_comments()
        self.assertEqual(
            self.convention_comments_service.return_status, utils.ReturnStatus.ERROR
        )
        self.assertTrue(self.convention_comments_service.form.has_error("comments"))

        self.convention_comments_service.request.POST = {
            "comments": "this is a new comment",
            "comments_files": (
                '{"bbfc7e3a-e0e7-4899-a1e1-fc632c3ea6b0": {"uuid": "bbfc7e3a-e0e7'
                + '-4899-a1e1-fc632c3ea6b0", "thumbnail": "data:image/png;base64,'
                + 'BLAH...BLAH...==", "size": 31185, "filename": "acquereur1.png"'
                + '}, "9e69e766-0167-4638-b1ce-f8f0b033e03a": {"uuid": "9e69e766-'
                + '0167-4638-b1ce-f8f0b033e03a", "thumbnail": "data:image/png;bas'
                + 'e64,BLAH...BLAH...==", "size": 69076, "filename": "acquereur2.'
                + 'png"}}'
            ),
        }

        self.convention_comments_service.save_comments()
        self.convention_comments_service.convention.refresh_from_db()
        comments = json.loads(self.convention_comments_service.convention.comments)
        self.assertEqual(
            self.convention_comments_service.return_status, utils.ReturnStatus.SUCCESS
        )
        self.assertEqual(comments["text"], "this is a new comment")
        self.assertEqual(
            comments["files"],
            {
                "bbfc7e3a-e0e7-4899-a1e1-fc632c3ea6b0": {
                    "uuid": "bbfc7e3a-e0e7-4899-a1e1-fc632c3ea6b0",
                    "thumbnail": "data:image/png;base64,BLAH...BLAH...==",
                    "size": 31185,
                    "filename": "acquereur1.png",
                },
                "9e69e766-0167-4638-b1ce-f8f0b033e03a": {
                    "uuid": "9e69e766-0167-4638-b1ce-f8f0b033e03a",
                    "thumbnail": "data:image/png;base64,BLAH...BLAH...==",
                    "size": 69076,
                    "filename": "acquereur2.png",
                },
            },
        )


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
        self.assertEqual(email_sent[1].to, ["fix@apilos.com"])
        self.assertEqual(email_sent[1].from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(
            email_sent[1].subject, f"Convention à instruire ({convention})"
        )
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent[1].body)

        User.objects.filter(username="raph").update(
            preferences_email=EmailPreferences.AUCUN
        )
        User.objects.filter(username="fix").update(
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
        email_service = EmailService()
        email_service.send_email_valide(
            "https://apilos.beta.gouv.fr/my_convention",
            convention,
            convention.get_email_bailleur_users(),
            ["me@apilos.com"],
        )
        email_sent = email_service.msg
        self.assertEqual(email_sent.to, ["raph@apilos.com"])
        self.assertEqual(email_sent.cc, ["me@apilos.com"])
        self.assertEqual(email_sent.from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(email_sent.subject, f"Convention validée ({convention})")
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
        email_service = EmailService()
        email_service.send_email_valide(
            "https://apilos.beta.gouv.fr/my_convention",
            convention,
            convention.get_email_bailleur_users(),
            ["me@apilos.com"],
        )
        email_sent = email_service.msg
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
        User.objects.filter(username="fix").update(
            preferences_email=EmailPreferences.AUCUN
        )

        email_service = EmailService()
        email_service.send_email_valide(
            "https://apilos.beta.gouv.fr/my_convention",
            convention,
            convention.get_email_bailleur_users(),
            ["me@apilos.com"],
        )
        email_sent = email_service.msg
        self.assertEqual(email_sent.to, ["contact@apilos.beta.gouv.fr"])
        self.assertEqual(email_sent.cc, [])
        self.assertEqual(email_sent.from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(
            email_sent.subject,
            f"[ATTENTION pas de destinataire à cet email] Convention validée ({convention})",
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

        self.assertEqual(email_sent.to, ["fix@apilos.com"])
        self.assertEqual(email_sent.cc, [])
        self.assertEqual(email_sent.from_email, "contact@apilos.beta.gouv.fr")
        self.assertEqual(email_sent.subject, f"Convention modifiée ({convention})")
        self.assertIn("https://apilos.beta.gouv.fr/my_convention", email_sent.body)
        self.assertNotIn("Toto à un vélo", email_sent.body)

        User.objects.filter(username="raph").update(
            preferences_email=EmailPreferences.AUCUN
        )
        User.objects.filter(username="fix").update(
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


class ServicesUtilsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    # set session in request object
    def setUp(self):
        self.request = RequestFactory().get("/conventions")
        middleware = SessionMiddleware(None)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_editable_convention(self):

        convention = Convention.objects.get(numero="0001")
        convention.statut = ConventionStatut.PROJET
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(utils.editable_convention(self.request, convention))
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertTrue(utils.editable_convention(self.request, convention))
        self.request.session["currently"] = GroupProfile.STAFF
        self.assertTrue(utils.editable_convention(self.request, convention))

        for statut in [ConventionStatut.INSTRUCTION, ConventionStatut.CORRECTION]:
            convention.statut = statut
            self.request.session["currently"] = GroupProfile.INSTRUCTEUR
            self.assertTrue(utils.editable_convention(self.request, convention))
            self.request.session["currently"] = GroupProfile.BAILLEUR
            self.assertFalse(utils.editable_convention(self.request, convention))
            self.request.session["currently"] = GroupProfile.STAFF
            self.assertTrue(utils.editable_convention(self.request, convention))

        for statut in [ConventionStatut.A_SIGNER, ConventionStatut.SIGNEE]:
            convention.statut = statut
            self.request.session["currently"] = GroupProfile.INSTRUCTEUR
            self.assertFalse(utils.editable_convention(self.request, convention))
            self.request.session["currently"] = GroupProfile.BAILLEUR
            self.assertFalse(utils.editable_convention(self.request, convention))
            self.request.session["currently"] = GroupProfile.STAFF
            self.assertFalse(utils.editable_convention(self.request, convention))
