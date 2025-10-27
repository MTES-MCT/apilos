from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

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

    def setUp(self):

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

    @mock.patch("conventions.views.conventions_mix.switch_is_active")
    def test_redirects_to_search_when_switch_off(self, mock_switch):
        mock_switch.return_value = False
        request = self.factory.post(reverse("conventions:search"), data={})
        response = ConventionMix.as_view()(request)
        # Should redirect to search when switch is off
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("conventions:search"), response["Location"])

    @mock.patch("conventions.views.conventions_mix.switch_is_active")
    @mock.patch("conventions.models.convention.switch_is_active")  # ADD THIS LINE
    @mock.patch("conventions.views.conventions_mix.UUIDListForm")
    def test_create_action_groups_and_redirects(
        self, mock_form, mock_switch_model, mock_switch_view
    ):
        mock_switch_view.return_value = True
        mock_switch_model.return_value = True
        self.assertEqual(self.convention_plai.lots.count(), 1)
        self.assertEqual(self.convention_plus.lots.count(), 1)

        data = {
            "uuids": [str(self.convention_plai.uuid), str(self.convention_plus.uuid)],
            "action": "create",
        }

        mock_form_instance = mock_form.return_value
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.cleaned_data = data

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

        self.assertIsNotNone(self.programme_2)
