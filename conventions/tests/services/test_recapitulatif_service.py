from datetime import date
from unittest import mock
from unittest.mock import patch

from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.test import RequestFactory, TestCase

from comments.models import Comment, CommentStatut
from conventions.forms.convention_number import ConventionNumberForm
from conventions.forms.programme_number import ProgrammeNumberForm
from conventions.models import Convention
from conventions.models.choices import ConventionStatut
from conventions.services import recapitulatif, utils
from conventions.services.utils import ReturnStatus
from programmes.models.models import Lot, Programme
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient
from users.models import User
from users.type_models import EmailPreferences


class ConventionRecapitulatifServiceTests(TestCase):
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
        self.request = HttpRequest()
        self.convention = Convention.objects.get(numero="0001")
        self.user = User.objects.get(username="fix")
        self.request.user = self.user
        self.service = recapitulatif.ConventionRecapitulatifService(
            convention=self.convention, request=self.request
        )

    def test_get_convention_recapitulatif(self):
        result = self.service.get_convention_recapitulatif()

        self.assertIsInstance(result["conventionNumberForm"], ConventionNumberForm)
        self.assertEqual(
            result["conventionNumberForm"].initial["convention_numero"],
            self.service.convention.numero,
        )

        self.assertIsInstance(result["programmeNumberForm"], ProgrammeNumberForm)
        self.assertEqual(
            result["programmeNumberForm"].initial["numero_galion"],
            self.service.convention.programme.numero_galion,
        )

    def test_get_convention_recapitulatif_incompleted_avenant_parent(self):
        avenant = self.convention.clone(self.user, convention_origin=self.convention)
        service_avenant = recapitulatif.ConventionRecapitulatifService(
            convention=avenant, request=self.request
        )
        programme = Programme.objects.get(pk=1)
        dummy_lot = Lot.objects.get(pk=1)
        dummy_lot.pk = None
        dummy_lot.nb_logements = 69
        dummy_lot.save()

        with patch.object(
            Convention, "is_incompleted_avenant_parent"
        ) as mock_is_incompleted_avenant_parent:
            mock_is_incompleted_avenant_parent.return_value = True

            with patch.object(Convention, "programme", programme):
                with patch.object(Convention, "lot", dummy_lot):
                    with patch.object(Programme, "ville", programme):
                        result = service_avenant.get_convention_recapitulatif()

                        self.assertEqual(
                            result["complete_for_avenant_form"].initial["ville"],
                            "Paris",
                        )
                        self.assertEqual(
                            result["complete_for_avenant_form"].initial["nb_logements"],
                            69,
                        )

    def test_get_convention_recapitulatif_comments(self):
        result = self.service.get_convention_recapitulatif()
        self.assertEqual(result["opened_comments"].count(), 0)
        Comment.objects.create(
            user_id=self.user.id,
            convention=self.convention,
            statut=CommentStatut.OUVERT,
        )
        Comment.objects.create(
            user_id=self.user.id,
            convention=self.convention,
            statut=CommentStatut.RESOLU,
        )
        self.assertEqual(result["opened_comments"].count(), 1)

    def test_update_programme_number_success(self):
        self.service.request.POST = {
            "numero_galion": "0" * 255,
            "update_programme_number": "1",
        }
        self.service.update_programme_number()

        self.assertEqual(self.convention.programme.numero_galion, "0" * 255)

    def test_update_programme_number_failed(self):
        self.service.request.POST = {
            "numero_galion": "0" * 256,
            "update_programme_number": "1",
        }
        result = self.service.update_programme_number()

        self.assertFalse(result["conventionNumberForm"].has_error("numero_galion"))

    def test_convention_submit(self):
        result = recapitulatif.convention_submit(self.request, self.convention)
        self.assertEqual(result["success"], utils.ReturnStatus.REFRESH)
        self.assertEqual(result["convention"], self.convention)

        self.request.POST = {"BackToInstruction": True}
        result = recapitulatif.convention_submit(self.request, self.convention)
        self.assertEqual(result["success"], utils.ReturnStatus.ERROR)


class AvenantRecapitulatifServiceTests(TestCase):
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
        self.request = HttpRequest()

        self.request.user = User.objects.get(username="fix")
        self.convention1 = Convention.objects.get(numero="0001")
        # set service with avenant
        self.avenant1 = self.convention1.clone(
            self.request.user, convention_origin=self.convention1
        )
        self.service = recapitulatif.ConventionRecapitulatifService(
            convention=self.avenant1, request=self.request
        )

    def test_update_avenant_number_success(self):
        self.service.request.POST = {
            "numero_galion": "a" * 255,
            "update_programme_number": "1",
        }
        self.service.update_programme_number()
        self.convention1.refresh_from_db()

        self.assertEqual(self.avenant1.programme.numero_galion, "a" * 255)
        self.assertEqual(self.convention1.programme.numero_galion, "a" * 255)

    def test_update_convention_number_success(self):
        self.service.convention = self.convention1
        self.service.request.POST = {
            "numero_galion": "b" * 255,
            "update_programme_number": "1",
        }
        self.service.update_programme_number()
        self.avenant1.refresh_from_db()

        self.assertEqual(self.convention1.programme.numero_galion, "b" * 255)
        self.assertEqual(self.avenant1.programme.numero_galion, "b" * 255)

    def test_convention_denonciation_validate(self):
        self.avenant1.date_denonciation = date(2022, 12, 31)
        self.avenant1.save()
        denonciation_result = recapitulatif.convention_denonciation_validate(
            self.request, self.avenant1.uuid
        )
        self.avenant1.refresh_from_db()
        self.convention1.refresh_from_db()

        self.assertEqual(denonciation_result["success"], utils.ReturnStatus.SUCCESS)
        self.assertEqual(self.convention1.date_denonciation, date(2022, 12, 31))
        self.assertEqual(self.convention1.statut, ConventionStatut.DENONCEE.label)
        self.assertEqual(self.avenant1.statut, ConventionStatut.DENONCEE.label)


class CollectInstructeurEmailsTestCase(TestCase):
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
        self.factory = RequestFactory()
        self.convention = Convention.objects.get(numero="0001")
        self.user = User.objects.get(username="fix")
        get_response = mock.MagicMock()
        self.request = self.factory.get("/")
        self.request.user = self.user
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()
        self.request.session["habilitation_id"] = "123"

    def test_collect_instructeur_emails(self):
        (instructeur_emails, _) = recapitulatif.collect_instructeur_emails(
            self.request, self.convention
        )

        self.assertIn(self.user.email, instructeur_emails)

    def test_collect_instructeur_cerbere_user_empty(self):
        with patch.object(User, "is_cerbere_user") as mock_is_cerbere_user:
            mock_is_cerbere_user.return_value = True
            with patch.object(SIAPClient, "get_instance") as mock_get_instance:
                mock_instance = mock_get_instance.return_value
                mock_instance.get_operation.return_value = {
                    "gestionnaireSecondaire": {"utilisateurs": []}
                }
                (instructeur_emails, _) = recapitulatif.collect_instructeur_emails(
                    self.request, self.convention
                )

                self.assertEqual([], instructeur_emails)

    def test_collect_instructeur_cerbere_user(self):
        with patch.object(User, "is_cerbere_user") as mock_is_cerbere_user:
            mock_is_cerbere_user.return_value = True
            with patch.object(SIAPClient, "get_instance") as mock_get_instance:
                mock_instance = mock_get_instance.return_value
                mock_instance.get_operation.return_value = {
                    "gestionnaireSecondaire": {
                        "utilisateurs": [
                            {
                                "email": "user0@STAFF.com",
                                "groupes": [{"profil": {"code": "STAFF"}}],
                            },
                            {
                                "email": "user0@BAILLEUR.com",
                                "groupes": [{"profil": {"code": "BAILLEUR"}}],
                            },
                            {
                                "email": "user0@INSTRUCTEUR.com",
                                "groupes": [{"profil": {"code": "INSTRUCTEUR"}}],
                            },
                            {
                                "email": "user0@ADM_CENTRALE.com",
                                "groupes": [{"profil": {"code": "ADM_CENTRALE"}}],
                            },
                            {
                                "email": "user0@DIR_REG.com",
                                "groupes": [{"profil": {"code": "DIR_REG"}}],
                            },
                            {
                                "email": "user1@SER_DEP.com",
                                "groupes": [{"profil": {"code": "SER_DEP"}}],
                            },
                            {
                                "email": "user1@SER_GEST.com",
                                "groupes": [{"profil": {"code": "SER_GEST"}}],
                            },
                            {
                                "email": "user0@ASS_HLM.com",
                                "groupes": [{"profil": {"code": "ASS_HLM"}}],
                            },
                            {
                                "email": "user0@MO_PERS_MORALE.com",
                                "groupes": [{"profil": {"code": "MO_PERS_MORALE"}}],
                            },
                            {
                                "email": "user0@MO_PERS_PHYS.com",
                                "groupes": [{"profil": {"code": "MO_PERS_PHYS"}}],
                            },
                        ]
                    }
                }

                (instructeur_emails, _) = recapitulatif.collect_instructeur_emails(
                    self.request, self.convention
                )

                self.assertEqual(["user1@SER_GEST.com"], instructeur_emails)

    def test_collect_instructeur_cerbere_user_multiprofil(self):
        with patch.object(User, "is_cerbere_user") as mock_is_cerbere_user:
            mock_is_cerbere_user.return_value = True
            with patch.object(SIAPClient, "get_instance") as mock_get_instance:
                mock_instance = mock_get_instance.return_value
                mock_instance.get_operation.return_value = {
                    "gestionnaireSecondaire": {
                        "utilisateurs": [
                            {
                                "email": "user2@SER_GEST.com",
                                "groupes": [
                                    {"profil": {"code": "STAFF"}},
                                    {"profil": {"code": "BAILLEUR"}},
                                    {"profil": {"code": "INSTRUCTEUR"}},
                                    {"profil": {"code": "ADM_CENTRALE"}},
                                    {"profil": {"code": "DIR_REG"}},
                                    {"profil": {"code": "SER_DEP"}},
                                    {"profil": {"code": "SER_GEST"}},
                                    {"profil": {"code": "ASS_HLM"}},
                                    {"profil": {"code": "MO_PERS_MORALE"}},
                                    {"profil": {"code": "MO_PERS_PHYS"}},
                                ],
                            },
                        ]
                    }
                }

                (instructeur_emails, _) = recapitulatif.collect_instructeur_emails(
                    self.request, self.convention
                )

                self.assertEqual(["user2@SER_GEST.com"], instructeur_emails)

    def test_collect_instructeur_cerbere_user_emailpref_aucun(self):
        User.objects.create(
            email="user3@SER_GEST.com", preferences_email=EmailPreferences.AUCUN
        )
        with patch.object(User, "is_cerbere_user") as mock_is_cerbere_user:
            mock_is_cerbere_user.return_value = True
            with patch.object(SIAPClient, "get_instance") as mock_get_instance:
                mock_instance = mock_get_instance.return_value
                mock_instance.get_operation.return_value = {
                    "gestionnaireSecondaire": {
                        "utilisateurs": [
                            {
                                "email": "user3@SER_GEST.com",
                                "groupes": [{"profil": {"code": "SER_GEST"}}],
                            },
                            {
                                "email": "user4@SER_GEST.com",
                                "groupes": [{"profil": {"code": "SER_GEST"}}],
                            },
                        ]
                    }
                }

                (instructeur_emails, _) = recapitulatif.collect_instructeur_emails(
                    self.request, self.convention
                )

                self.assertEqual(["user4@SER_GEST.com"], instructeur_emails)

    def test_collect_instructeur_cerbere_user_raise_siapexception(self):
        with patch.object(User, "is_cerbere_user") as mock_is_cerbere_user:
            mock_is_cerbere_user.return_value = True
            with patch.object(SIAPClient, "get_instance") as mock_get_instance:
                mock_get_instance.side_effect = SIAPException("Test exception")

                (
                    instructeur_emails,
                    submitted,
                ) = recapitulatif.collect_instructeur_emails(
                    self.request, self.convention
                )

                self.assertEqual([], instructeur_emails)
                self.assertEqual(ReturnStatus.WARNING, submitted)
