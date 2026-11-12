from unittest.mock import patch

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from comments.models import Comment, CommentStatut
from conventions.models import AvenantType, ConventionStatut
from conventions.tests.views.abstract import AbstractCreateViewTestCase
from programmes.models import Annexe, Logement, Lot
from users.models import User


class ConventionRecapitulatifTests(AbstractCreateViewTestCase, TestCase):
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

        self.target_path = reverse(
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )
        self.post_success_http_code = 200
        self.target_template = "conventions/recapitulatif.html"
        self.error_payload = {
            "numero_operation": "0" * 256,
            "update_programme_number": "1",
        }
        self.success_payload = {
            "numero_operation": "0" * 255,
            "update_programme_number": "1",
        }
        self.msg_prefix = "[ConventionRecapitulatifTests] "

    def test_post_param_calls_the_correct_service_method(self):
        self.client.login(username="nicolas", password="12345")

        for post_param, expected in (
            ("update_programme_number", "update_programme_number"),
            ("update_convention_number", "update_convention_number"),
            ("cancel_convention", "cancel_convention"),
            ("reactive_convention", "reactive_convention"),
            (None, "save_convention_type_1_and_2"),
        ):
            with patch(
                "conventions.views.conventions.ConventionRecapitulatifService",
                autospec=True,
            ) as mock_service:
                response = self.client.post(
                    self.target_path, data={post_param: "1"} if post_param else {}
                )
                self.assertEqual(response.status_code, 200)

            self.assertEqual(len(mock_service.method_calls), 1)
            self.assertEqual(mock_service.method_calls[0][0], f"().{expected}")

    def test_refresh_opened_comments_frame(self):
        convention = self.convention_75
        convention.statut = ConventionStatut.INSTRUCTION.label
        convention.save()
        url = reverse("conventions:recapitulatif_commentaires", args=[convention.uuid])
        self.assertEqual(self.client.get(url).status_code, 302)
        user = User.objects.get(username="fix")
        self.client.force_login(user)
        response = self.client.get(url)
        self.assertContains(response, 'id="opened_comments_block"')
        self.assertContains(response, 'id="refresh_opened_comments_empty"')
        comment = Comment.objects.create(
            user=user,
            convention=convention,
            statut=CommentStatut.OUVERT,
            message="Commentaire ouvert pour le test",
        )
        response = self.client.get(url)
        self.assertContains(response, "Commentaire ouvert pour le test")
        self.assertContains(response, 'id="refresh_opened_comments_main"')
        comment.statut = CommentStatut.RESOLU
        comment.save()
        response = self.client.get(url)
        self.assertNotContains(response, "Commentaire ouvert pour le test")
        self.assertContains(response, 'id="refresh_opened_comments_empty"')
        self.client.force_login(User.objects.get(username="roger"))
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_avenant_logements_and_annexes_queries_do_not_grow_per_row(self):
        user = User.objects.get(username="fix")
        avenant = self.convention_75.clone(user, convention_origin=self.convention_75)
        avenant.avenant_types.add(AvenantType.objects.get(nom="logements"))
        avenant.statut = ConventionStatut.INSTRUCTION.label
        avenant.save()
        lot = avenant.lot
        lot.logements.all().delete()
        self.client.force_login(user)
        url = reverse("conventions:recapitulatif", args=[avenant.uuid])

        def add_logements(start, count):
            logements = Logement.objects.bulk_create(
                [
                    Logement(
                        lot=lot,
                        designation=f"TEST-{index:04d}",
                        typologie="T1",
                        surface_habitable=30,
                        surface_corrigee=30 if index % 2 else None,
                        loyer=100 if index % 4 < 2 else None,
                        import_order=index,
                    )
                    for index in range(start, start + count)
                ]
            )
            Annexe.objects.bulk_create(
                [
                    Annexe(
                        logement=logement,
                        surface_hors_surface_retenue=2,
                        loyer_par_metre_carre=3,
                        loyer=6,
                    )
                    for logement in logements
                ]
            )

        add_logements(0, 4)
        with CaptureQueriesContext(connection) as few_queries:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        add_logements(4, 24)
        with CaptureQueriesContext(connection) as many_queries:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(many_queries), len(few_queries) + 2)
        for index in range(28):
            self.assertContains(response, f"TEST-{index:04d}")
        self.assertContains(response, "Surface corrigée")
        self.assertContains(response, "Annexes")
        self.assertContains(response, "new CommentFactory")

    def test_avenant_recap_with_many_logements(self):
        user = User.objects.get(username="fix")
        avenant = self.convention_75.clone(user, convention_origin=self.convention_75)
        avenant.avenant_types.add(AvenantType.objects.get(nom="logements"))
        lot = avenant.lot
        lot.logements.all().delete()
        Logement.objects.bulk_create(
            [
                Logement(
                    lot=lot,
                    designation=f"LARGE-{index:04d}",
                    typologie="T1",
                    surface_habitable=30,
                    surface_corrigee=30,
                    loyer=100,
                    import_order=index,
                )
                for index in range(1048)
            ]
        )
        self.client.force_login(user)
        response = self.client.get(
            reverse("conventions:recapitulatif", args=[avenant.uuid])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LARGE-0000")
        self.assertContains(response, "LARGE-1047")
        self.assertEqual(len(response.context["recap_logements_corrigee"]), 1048)

    def test_convention_annexes_queries_do_not_grow_per_row(self):
        lot = self.convention_75.lot
        lot.logements.all().delete()
        self._login_as_superuser()

        def add_annexes(start, count):
            logements = Logement.objects.bulk_create(
                [
                    Logement(
                        lot=lot,
                        designation=f"ANNEXE-{index:04d}",
                        typologie="T1",
                        loyer=100,
                    )
                    for index in range(start, start + count)
                ]
            )
            Annexe.objects.bulk_create(
                [
                    Annexe(
                        logement=logement,
                        surface_hors_surface_retenue=2,
                        loyer_par_metre_carre=3,
                        loyer=6,
                    )
                    for logement in logements
                ]
            )

        add_annexes(0, 2)
        with CaptureQueriesContext(connection) as few_queries:
            response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ANNEXE-0000", count=2)
        add_annexes(2, 20)
        with CaptureQueriesContext(connection) as many_queries:
            response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ANNEXE-0021", count=2)
        self.assertLessEqual(len(many_queries), len(few_queries) + 2)

    def test_recap_logements_preserves_categories_and_order_across_lots(self):
        lot = self.convention_75.lot
        lot.logements.all().delete()
        second_lot = Lot.objects.create(
            convention=self.convention_75, financement="PLAI"
        )
        for current_lot in (lot, second_lot):
            for index in range(8):
                Logement.objects.create(
                    lot=current_lot,
                    designation=f"{current_lot.financement}-{index}",
                    typologie="T1",
                    surface_corrigee=20 if index % 2 else None,
                    loyer=10 if index % 4 < 2 else None,
                    import_order=None if index == 0 else 8 - index,
                )
        self._login_as_superuser()
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200)
        convention = response.context["convention"]
        for context_key, property_name in (
            ("recap_logements", "logements_import_ordered"),
            ("recap_logements_sans_loyer", "logements_sans_loyer_import_ordered"),
            ("recap_logements_corrigee", "logements_corrigee_import_ordered"),
            (
                "recap_logements_corrigee_sans_loyer",
                "logements_corrigee_sans_loyer_import_ordered",
            ),
        ):
            self.assertEqual(
                [logement.pk for logement in response.context[context_key]],
                [logement.pk for logement in getattr(convention, property_name)],
            )

    def test_validation_error_renders_logements(self):
        lot = self.convention_75.lot
        Logement.objects.create(
            lot=lot,
            designation="VALIDATION-TEST",
            typologie="T1",
            surface_habitable=30,
            loyer=100,
        )
        self._login_as_superuser()
        response = self.client.post(
            reverse("conventions:validate", args=[self.convention_75.uuid]),
            {"completeform": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VALIDATION-TEST")
