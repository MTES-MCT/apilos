from decimal import Decimal

from django.forms import ValidationError, model_to_dict
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase

from conventions.forms import (
    FoyerResidenceLogementFormSet,
    LogementCorrigeeFormSet,
    LogementFormSet,
    LotFoyerResidenceLgtsDetailsForm,
    LotLgtsOptionFormSet,
    UploadForm,
)
from conventions.models import Convention
from conventions.services import utils
from conventions.services.logements import (
    ConventionFoyerResidenceLogementsService,
    ConventionLogementsService,
)
from conventions.tests.fixtures import (
    foyer_residence_logements_success_payload,
    logement_success_payload,
)
from programmes.models import Logement, LogementEDD, NatureLogement
from users.models import User


class ConventionLogementsServiceTests(TestCase):
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
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        for lot in convention.lots.all():
            lot.nb_logements = 2
            lot.save()
        request.user = User.objects.get(username="fix")
        self.service = ConventionLogementsService(
            convention=convention, request=request
        )

        avenant = convention.clone(request.user, convention_origin=convention)
        self.service_avenant = ConventionLogementsService(
            convention=avenant, request=request
        )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(
            self.service.formset_convention_mixte, LotLgtsOptionFormSet
        )

        for form in self.service.formset_convention_mixte:
            lot = self.service.convention.lots.get(
                financement=form.initial["financement"]
            )
            for lot_field in [
                "uuid",
                "financement",
                "lgts_mixite_sociale_negocies",
                "loyer_derogatoire",
                "surface_locaux_collectifs_residentiels",
                "loyer_associations_foncieres",
                "nb_logements",
            ]:
                self.assertEqual(
                    form.initial[lot_field],
                    getattr(lot, lot_field),
                )
        self.assertIsInstance(self.service.formset, LogementFormSet)
        self.assertIsInstance(self.service.upform, UploadForm)

    def test_get_prefetches_logements_in_import_order(self):
        lot = self.service.convention.lot
        lot.logements.all().delete()
        Logement.objects.bulk_create(
            [
                Logement(lot=lot, designation="B2", typologie="T1", import_order=2),
                Logement(lot=lot, designation="B1", typologie="T1", import_order=1),
            ]
        )
        with self.assertNumQueries(2):
            self.service.get()
        self.assertEqual(
            [form.initial["designation"] for form in self.service.formset_sans_loyer],
            ["B1", "B2"],
        )

    def test_number_input_script_only_when_callback_is_provided(self):
        form = LogementFormSet(initial=[{}]).forms[0]
        request = HttpRequest()
        request.session = {}
        context = {"form_input": form["surface_habitable"], "request": request}
        without_callback = render_to_string("common/form/input_number.html", context)
        with_callback = render_to_string(
            "common/form/input_number.html",
            {**context, "onchange": "compute_total_value('sh')"},
        )
        self.assertNotIn("DOMContentLoaded", without_callback)
        self.assertIn("compute_total_value(&#x27;sh&#x27;)", with_callback)

    def test_save(self):
        self.service.request.POST = {
            "nb_logements": "2",
            "lots-0-uuid": str(self.service.convention.lot.uuid),
            **logement_success_payload,
        }

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

        logement_b1 = Logement.objects.prefetch_related("lot").get(
            lot=self.service.convention.lots.get(
                financement=logement_success_payload["lots-0-financement"]
            ),
            designation="B1",
        )

        self.assertEqual(
            model_to_dict(
                logement_b1,
                fields=[
                    "designation",
                    "typologie",
                    "surface_habitable",
                    "surface_annexes",
                    "surface_annexes_retenue",
                    "surface_utile",
                    "loyer_par_metre_carre",
                    "coeficient",
                    "loyer",
                    "import_order",
                ],
            ),
            {
                "designation": "B1",
                "typologie": "T1",
                "surface_habitable": Decimal("12.12"),
                "surface_annexes": Decimal("45.57"),
                "surface_annexes_retenue": Decimal("0.00"),
                "surface_utile": Decimal("30.00"),
                "loyer_par_metre_carre": Decimal("4.5"),
                "coeficient": Decimal("1.0000"),
                "loyer": Decimal("135.00"),
                "import_order": 0,
            },
        )
        self.assertEqual(logement_b1.lot.loyer_derogatoire, 10.00)
        self.assertEqual(logement_b1.lot.surface_locaux_collectifs_residentiels, 25.00)
        self.assertEqual(logement_b1.lot.loyer_associations_foncieres, 30.00)
        self.assertEqual(logement_b1.lot.lgts_mixite_sociale_negocies, 2)

    def test_save_fails_on_nb_logements(self):
        self.service.request.POST = {
            "lots-0-uuid": str(self.service.convention.lot.uuid),
            **logement_success_payload,
        }

        self.service.request.POST["lots-0-nb_logements"] = "3"
        self.service.save()
        assert self.service.formset.optional_errors == [
            ValidationError(
                "Le nombre de logement à conventionner (3) ne correspond pas au nombre de logements déclaré (2)"
            )
        ]
        assert self.service.formset.non_form_errors() == []

    def test_save_fails_on_nb_logements_avenants(self):
        self.service_avenant.request.POST = {
            "uuid": str(self.service_avenant.convention.lot.uuid),
            **logement_success_payload,
        }
        self.service_avenant.request.POST["lots-0-nb_logements"] = "3"
        self.service_avenant.save()
        assert self.service_avenant.formset.optional_errors == [
            ValidationError(
                "Le nombre de logement à conventionner (3) ne correspond pas au nombre de logements déclaré (2)"
            )
        ]
        assert self.service_avenant.formset.non_form_errors() == []

    def test_edd_validation_queries_and_errors(self):
        lot = self.service.convention.lot
        programme = self.service.convention.programme
        LogementEDD.objects.filter(programme=programme).delete()
        LogementEDD.objects.bulk_create(
            [
                LogementEDD(programme=programme, designation="B1", financement="PLUS"),
                LogementEDD(programme=programme, designation="B2", financement="PLAI"),
                LogementEDD(programme=programme, designation="B3", financement="PLUS"),
                LogementEDD(programme=programme, designation="B3", financement="PLUS"),
            ]
        )
        data = {"form-TOTAL_FORMS": "4", "form-INITIAL_FORMS": "4"}
        for index in range(4):
            data.update(
                {
                    f"form-{index}-designation": f"B{index + 1}",
                    f"form-{index}-financement": "PLUS",
                    f"form-{index}-typologie": "T1",
                    f"form-{index}-surface_habitable": "30",
                    f"form-{index}-surface_corrigee": "30",
                    f"form-{index}-loyer_par_metre_carre": "4.5",
                    f"form-{index}-coeficient": "1",
                    f"form-{index}-loyer": "135",
                }
            )
        formset = LogementCorrigeeFormSet(data)
        formset.lot_id = lot.id
        formset.programme_id = programme.id
        with self.assertNumQueries(3):
            self.assertFalse(formset.is_valid())
        self.assertNotIn("designation", formset.forms[0].errors)
        self.assertIn("déclaré comme PLAI", formset.forms[1].errors["designation"][0])
        self.assertIn(
            "présent plusieurs fois", formset.forms[2].errors["designation"][0]
        )
        self.assertIn("n'est pas dans l'EDD", formset.forms[3].errors["designation"][0])

    def test_save_many_corrected_logements(self):
        service = self.service_avenant
        lot = service.convention.lot
        lot.logements.all().delete()
        logements = [
            Logement(
                lot=lot,
                designation=f"B{index}",
                typologie="T1",
                surface_habitable=30,
                surface_corrigee=30,
                loyer_par_metre_carre=Decimal("4.5"),
                coeficient=1,
                loyer=135,
                import_order=index,
            )
            for index in range(1048)
        ]
        Logement.objects.bulk_create(logements)
        data = {
            **logement_success_payload,
            "avec_loyer-TOTAL_FORMS": "0",
            "avec_loyer-INITIAL_FORMS": "0",
            "corrigee_avec_loyer-TOTAL_FORMS": str(len(logements)),
            "corrigee_avec_loyer-INITIAL_FORMS": str(len(logements)),
            "lots-0-uuid": str(lot.uuid),
            "lots-0-financement": lot.financement,
            "lots-0-nb_logements": str(len(logements)),
            "ignore_optional_errors": "1",
        }
        for index, logement in enumerate(logements):
            prefix = f"corrigee_avec_loyer-{index}"
            data.update(
                {
                    f"{prefix}-uuid": str(logement.uuid),
                    f"{prefix}-designation": logement.designation,
                    f"{prefix}-financement": lot.financement,
                    f"{prefix}-typologie": "T1",
                    f"{prefix}-surface_habitable": "30",
                    f"{prefix}-surface_corrigee": "30",
                    f"{prefix}-loyer_par_metre_carre": "4.5",
                    f"{prefix}-coeficient": "1",
                    f"{prefix}-loyer": "135",
                    f"{prefix}-import_order": str(index),
                }
            )
        data["corrigee_avec_loyer-1047-surface_corrigee"] = "31"
        data["corrigee_avec_loyer-1047-loyer"] = "139.5"
        service.request.POST = data
        service.save()

        self.assertEqual(service.return_status, utils.ReturnStatus.SUCCESS)
        self.assertEqual(lot.logements.count(), len(logements))
        logement = lot.logements.get(uuid=logements[-1].uuid)
        self.assertEqual(logement.surface_corrigee, Decimal("31"))
        self.assertEqual(logement.loyer, Decimal("139.50"))
        self.assertEqual(logement.import_order, 1047)


class ConventionFoyerResidenceLogementsServiceTests(TestCase):
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
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        # convention is foyer
        convention = Convention.objects.get(numero="0001")
        convention.programme.nature_logement = NatureLogement.AUTRE
        convention.programme.save()
        lot_convention = convention.lot
        lot_convention.nb_logements = 2
        lot_convention.save()

        request.user = User.objects.get(username="fix")
        self.service = ConventionFoyerResidenceLogementsService(
            convention=convention, request=request
        )

        avenant = convention.clone(request.user, convention_origin=convention)
        self.service_avenant = ConventionFoyerResidenceLogementsService(
            convention=avenant, request=request
        )

    def _get_lots_post_data(self, service=None, nb_logements="2"):
        service = service or self.service
        lot = service.convention.lot
        return {
            "lots-TOTAL_FORMS": "1",
            "lots-INITIAL_FORMS": "1",
            "lots-0-uuid": str(lot.uuid),
            "lots-0-financement": lot.financement,
            "lots-0-nb_logements": nb_logements,
            "lots-0-surface_habitable_totale": "50.55",
            "lots-0-lgts_mixite_sociale_negocies": "0",
            "lots-0-loyer_derogatoire": "",
            "lots-0-surface_locaux_collectifs_residentiels": "",
            "lots-0-loyer_associations_foncieres": "",
        }

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, LotFoyerResidenceLgtsDetailsForm)
        self.assertIsInstance(self.service.formset, FoyerResidenceLogementFormSet)
        self.assertIsInstance(
            self.service.formset_convention_mixte, LotLgtsOptionFormSet
        )
        self.assertIsInstance(self.service.upform, UploadForm)
        for lot_field in [
            "uuid",
            "surface_habitable_totale",
        ]:
            self.assertEqual(
                self.service.form.initial[lot_field],
                getattr(self.service.convention.lot, lot_field),
            )

    def test_save(self):
        self.service.request.POST = {
            "uuid": str(self.service.convention.lot.uuid),
            **foyer_residence_logements_success_payload,
            **self._get_lots_post_data(),
        }

        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

        logement_b1 = Logement.objects.prefetch_related("lot").get(
            lot=self.service.convention.lot, designation="B1"
        )

        self.assertEqual(
            model_to_dict(
                logement_b1,
                fields=[
                    "designation",
                    "typologie",
                    "surface_habitable",
                    "loyer",
                ],
            ),
            {
                "designation": "B1",
                "typologie": "T1prime",
                "surface_habitable": Decimal("12.12"),
                "loyer": Decimal("135.00"),
            },
        )
        self.assertEqual(logement_b1.lot.surface_habitable_totale, Decimal("50.55"))

    def test_save_fails_on_loyer(self):
        self.service.request.POST = {
            **foyer_residence_logements_success_payload,
            **self._get_lots_post_data(),
            "form-0-typologie": "T2",
            "form-0-loyer": "160.00",
            "form-1-typologie": "T2",
            "form-1-loyer": "161.00",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

    def test_save_fails_on_nb_logements(self):
        self.service.request.POST = {
            **foyer_residence_logements_success_payload,
            **self._get_lots_post_data(),
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "3",
            "form-2-uuid": "",
            "form-2-designation": "b2",
            "form-2-typologie": "T2",
            "form-2-surface_habitable": "16.00",
            "form-2-loyer": "160.00",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        assert self.service.formset.optional_errors == [
            ValidationError(
                "Le nombre de logement à conventionner (2) ne correspond pas au nombre de logements déclaré (3)"
            )
        ]
        assert self.service.formset.non_form_errors() == []

    def test_save_fails_on_nb_logements_avenant(self):

        self.service_avenant.request.POST = {
            **foyer_residence_logements_success_payload,
            **self._get_lots_post_data(service=self.service_avenant),
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "3",
            "form-2-uuid": "",
            "form-2-designation": "b2",
            "form-2-typologie": "T2",
            "form-2-surface_habitable": "16.00",
            "form-2-loyer": "160.00",
        }
        self.service_avenant.save()
        self.assertEqual(self.service_avenant.return_status, utils.ReturnStatus.ERROR)
        assert self.service_avenant.formset.optional_errors == [
            ValidationError(
                "Le nombre de logement à conventionner (2) ne correspond pas au nombre de logements déclaré (3)"
            )
        ]
        assert self.service_avenant.formset.non_form_errors() == []
