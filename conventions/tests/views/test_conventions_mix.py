from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from conventions.models.convention import Convention
from conventions.views.conventions_mix import ConventionMix
from core.tests.factories import (
    AnnexeFactory,
    ConventionFactory,
    LogementFactory,
    LotFactory,
    ProgrammeFactory,
)
from instructeurs.tests.factories import AdministrationFactory
from programmes.models.choices import (
    Financement,
    TypeHabitat,
    TypologieAnnexe,
    TypologieLogement,
)
from users.models import GroupProfile, User


class ConventionMixViewTests(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    @mock.patch("conventions.models.convention.switch_is_active")
    def setUp(self, mock_switch_model):
        mock_switch_model.return_value = True

        get_response = mock.MagicMock()
        self.request = RequestFactory().get("/")
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()

        self.factory = RequestFactory()
        programme_1 = ProgrammeFactory(
            administration=AdministrationFactory(code="admin1"),
            code_postal="10000",
            ville="Troyes",
        )
        self.programme_2 = ProgrammeFactory(
            administration=AdministrationFactory(code="admin2"),
            code_postal="10800",
            ville="La Vendue-Mignot",
        )
        self.convention_plai = ConventionFactory(programme=programme_1, numero="0001")
        self.convention_plus = ConventionFactory(programme=programme_1, numero="0002")
        # TODO : check with different TypeHabitat.MIXTE
        lot_plai = LotFactory(
            convention=self.convention_plai,
            financement=Financement.PLAI,
            type_habitat=TypeHabitat.COLLECTIF,
            nb_logements=None,
            make_upload_on_fields=["edd_volumetrique", "edd_classique"],
        )
        lot_plus = LotFactory(
            convention=self.convention_plus,
            financement=Financement.PLUS,
            type_habitat=TypeHabitat.COLLECTIF,
            nb_logements=None,
            make_upload_on_fields=["edd_volumetrique", "edd_classique"],
        )

        logement = LogementFactory(
            lot=lot_plai, designation="PLAI 1", typologie=TypologieLogement.T1
        )

        AnnexeFactory(
            logement=logement,
            typologie=TypologieAnnexe.COUR,
            surface_hors_surface_retenue=5,
            loyer_par_metre_carre=0.1,
        )

        AnnexeFactory(
            logement=logement,
            typologie=TypologieAnnexe.JARDIN,
            surface_hors_surface_retenue=5,
            loyer_par_metre_carre=0.1,
        )

        LogementFactory(
            lot=lot_plai, designation="PLAI 2", typologie=TypologieLogement.T2
        )
        LogementFactory(
            lot=lot_plai, designation="PLAI 3", typologie=TypologieLogement.T3
        )
        LogementFactory(
            lot=lot_plus, designation="PLUS 1", typologie=TypologieLogement.T1
        )

        self.convention_pls_programme_2 = ConventionFactory(
            programme=self.programme_2, numero="0003"
        )
        self.convention_plai_programme_2 = ConventionFactory(
            programme=self.programme_2, numero="0004"
        )

        lot_plai = LotFactory(
            convention=self.convention_pls_programme_2,
            financement=Financement.PLS,
            type_habitat=TypeHabitat.MIXTE,
            nb_logements=None,
            make_upload_on_fields=["edd_volumetrique", "edd_classique"],
        )
        lot_plus = LotFactory(
            convention=self.convention_plai_programme_2,
            financement=Financement.PLAI,
            type_habitat=TypeHabitat.MIXTE,
            nb_logements=None,
            make_upload_on_fields=["edd_volumetrique", "edd_classique"],
        )
        logement = LogementFactory(
            lot=lot_plai, designation="PLAI-PROG-2-1", typologie=TypologieLogement.T1
        )

        AnnexeFactory(
            logement=logement,
            typologie=TypologieAnnexe.TERRASSE,
            surface_hors_surface_retenue=5,
            loyer_par_metre_carre=12,
        )

        AnnexeFactory(
            logement=logement,
            typologie=TypologieAnnexe.COUR,
            surface_hors_surface_retenue=7,
            loyer_par_metre_carre=10,
        )

        LogementFactory(
            lot=lot_plai, designation="PLAI-PROG-2-2", typologie=TypologieLogement.T2
        )

        LogementFactory(
            lot=lot_plai, designation="PLAI-PROG-2-3", typologie=TypologieLogement.T3
        )

        LogementFactory(
            lot=lot_plus, designation="PLS-PROG-2-1", typologie=TypologieLogement.T1
        )

        self.mixed_convention_Programmp, _, self.mixed_convention = (
            Convention.objects.group_conventions(
                [
                    str(self.convention_pls_programme_2.uuid),
                    str(self.convention_plai_programme_2.uuid),
                ]
            )
        )
        self.mixed_convention.refresh_from_db()

    @mock.patch("conventions.views.conventions_mix.switch_is_active")
    def test_redirects_to_search_when_switch_off(self, mock_switch):
        mock_switch.return_value = False
        request = self.factory.post(reverse("conventions:search"), data={})
        response = ConventionMix.as_view()(request)
        # Should redirect to search when switch is off
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("conventions:search"), response["Location"])

    @mock.patch("conventions.views.conventions_mix.switch_is_active")
    @mock.patch("conventions.models.convention.switch_is_active")
    def test_create_action_groups_and_redirects(
        self, mock_switch_model, mock_switch_view
    ):
        mock_switch_view.return_value = True
        mock_switch_model.return_value = True
        self.assertEqual(self.convention_plai.lots.count(), 1)
        self.assertEqual(self.convention_plus.lots.count(), 1)

        data = {
            "uuids": [str(self.convention_plai.uuid), str(self.convention_plus.uuid)],
            "action": "create",
        }

        self.request = RequestFactory().post(
            reverse("conventions:convention_mix_init"), data=data
        )
        self.request.user = User.objects.get(username="raph")
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()
        self.request.session["currently"] = GroupProfile.BAILLEUR
        response = ConventionMix.as_view()(self.request)

        self.assertEqual(response.status_code, 302)
        expected_url = reverse(
            "programmes:operation_conventions",
            args=[self.convention_plai.programme.numero_operation],
        )
        self.assertEqual(response.url, expected_url)

        self.convention_plai.refresh_from_db()

        self.assertEqual(self.convention_plai.lots.count(), 2)

    @mock.patch("conventions.views.conventions_mix.switch_is_active")
    @mock.patch("conventions.models.convention.switch_is_active")
    def test_degroup_action_degroups_and_redirects(
        self, mock_switch_view, mock_switch_model
    ):
        mock_switch_view.return_value = True
        mock_switch_model.return_value = True
        self.assertEqual(self.mixed_convention.lots.count(), 2)

        data = {
            "uuids": [str(self.mixed_convention.uuid)],
            "action": "dispatch",
        }

        self.request = RequestFactory().post(
            reverse("conventions:convention_mix_init"), data=data
        )
        self.request.user = User.objects.get(username="raph")
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()
        self.request.session["currently"] = GroupProfile.BAILLEUR
        response = ConventionMix.as_view()(self.request)

        self.assertEqual(response.status_code, 302)
        expected_url = reverse(
            "programmes:operation_conventions",
            args=[self.convention_pls_programme_2.programme.numero_operation],
        )
        self.assertEqual(response.url, expected_url)
        self.assertEqual(self.mixed_convention.lots.count(), 0)

        degrouped_conventions = Convention.objects.filter(
            programme=self.programme_2,
        )
        self.assertEqual(degrouped_conventions.count(), 2)

        for convention in degrouped_conventions:
            self.assertEqual(convention.lots.all().count(), 1)

        self.assertEqual(
            [convention.lot.financement for convention in degrouped_conventions],
            [Financement.PLS.label, Financement.PLAI.label],
        )
