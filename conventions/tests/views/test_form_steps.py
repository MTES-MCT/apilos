from django.http.request import HttpRequest
from django.test import TestCase

from conventions.models import Convention
from conventions.views.convention_form import (
    ConventionFormSteps,
    administration_step,
    annexes_step,
    avenant_annexes_step,
    avenant_bailleur_step,
    avenant_champ_libre_step,
    avenant_collectif_step,
    avenant_commentaires_step,
    avenant_financement_step,
    avenant_foyer_residence_logements_step,
    avenant_logements_step,
    avenant_programme_step,
    bailleur_step,
    cadastre_step,
    collectif_step,
    commentaires_step,
    edd_step,
    financement_step,
    foyer_attribution_step,
    foyer_residence_logements_step,
    foyer_variante_step,
    logements_step,
    programme_step,
    residence_attribution_step,
    stationnements_step,
)
from programmes.models.choices import NatureLogement
from users.models import User


class ConventionFormStepsTests(TestCase):
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
        super().setUp()
        self.request = HttpRequest()
        self.convention = Convention.objects.first()
        self.user = User.objects.get(username="nicolas")
        self.request.user = self.user
        self.avenant = self.convention.clone(
            self.user, convention_origin=self.convention
        )

    def test_form_steps_basic(self):
        form_steps = ConventionFormSteps(
            convention=self.convention, request=self.request
        )
        self.assertEqual(
            form_steps.steps,
            [
                bailleur_step,
                programme_step,
                cadastre_step,
                edd_step,
                financement_step,
                logements_step,
                annexes_step,
                stationnements_step,
                administration_step,
                commentaires_step,
            ],
        )

    def test_avenant_foyer_steps(self):
        self.avenant.programme.nature_logement = NatureLogement.AUTRE
        self.avenant.programme.save()
        self.assertTrue(self.avenant.programme.is_foyer())

        form_steps = ConventionFormSteps(convention=self.avenant, request=self.request)
        self.assertEqual(
            form_steps.steps,
            [
                avenant_bailleur_step,
                avenant_programme_step,
                avenant_financement_step,
                avenant_foyer_residence_logements_step,
                avenant_collectif_step,
                avenant_champ_libre_step,
                avenant_commentaires_step,
            ],
        )

    def test_avenant_residence_steps(self):
        self.avenant.programme.nature_logement = NatureLogement.HEBERGEMENT
        self.avenant.programme.save()
        self.assertTrue(self.avenant.programme.is_residence())

        form_steps = ConventionFormSteps(convention=self.avenant, request=self.request)
        self.assertEqual(
            form_steps.steps,
            [
                avenant_bailleur_step,
                avenant_programme_step,
                avenant_financement_step,
                avenant_foyer_residence_logements_step,
                avenant_collectif_step,
                avenant_champ_libre_step,
                avenant_commentaires_step,
            ],
        )

    def test_avenant_bailleur_view_steps(self):
        form_steps = ConventionFormSteps(
            convention=self.avenant,
            request=self.request,
            active_classname="AvenantBailleurView",
        )
        self.assertEqual(form_steps.steps, [avenant_bailleur_step])

    def test_avenant_programme_view_steps(self):
        form_steps = ConventionFormSteps(
            convention=self.avenant,
            request=self.request,
            active_classname="AvenantProgrammeView",
        )
        self.assertEqual(form_steps.steps, [avenant_programme_step])

    def test_avenant_logements_or_annexes_view_steps(self):
        for classname in ["AvenantLogementsView", "AvenantAnnexesView"]:
            form_steps = ConventionFormSteps(
                convention=self.avenant,
                request=self.request,
                active_classname=classname,
            )

            self.assertEqual(
                form_steps.steps, [avenant_logements_step, avenant_annexes_step]
            )

    def test_avenant_foyer_or_collectif_residence_view_steps(self):
        for classname in [
            "AvenantFoyerResidenceLogementsView",
            "AvenantCollectifView",
        ]:
            form_steps = ConventionFormSteps(
                convention=self.avenant,
                request=self.request,
                active_classname=classname,
            )

            self.assertEqual(
                form_steps.steps,
                [avenant_foyer_residence_logements_step, avenant_collectif_step],
            )

    def test_avenant_financement_view_steps(self):
        form_steps = ConventionFormSteps(
            convention=self.avenant,
            request=self.request,
            active_classname="AvenantFinancementView",
        )
        self.assertEqual(form_steps.steps, [avenant_financement_step])

    def test_avenant_champ_libre_view_steps(self):
        form_steps = ConventionFormSteps(
            convention=self.avenant,
            request=self.request,
            active_classname="AvenantChampLibreView",
        )
        self.assertEqual(form_steps.steps, [avenant_champ_libre_step])

    def test_avenant_comments_view_steps(self):
        form_steps = ConventionFormSteps(
            convention=self.avenant,
            request=self.request,
            active_classname="AvenantCommentsView",
        )
        self.assertEqual(form_steps.steps, [avenant_commentaires_step])

    def test_programme_foyer_steps(self):
        self.convention.programme.nature_logement = NatureLogement.AUTRE
        self.convention.programme.save()
        self.assertTrue(self.convention.programme.is_foyer())

        form_steps = ConventionFormSteps(
            convention=self.convention, request=self.request
        )

        self.assertEqual(
            form_steps.steps,
            [
                bailleur_step,
                programme_step,
                cadastre_step,
                edd_step,
                financement_step,
                foyer_residence_logements_step,
                collectif_step,
                foyer_attribution_step,
                foyer_variante_step,
                administration_step,
                commentaires_step,
            ],
        )

    def test_programme_residence_steps(self):
        self.convention.programme.nature_logement = NatureLogement.HEBERGEMENT
        self.convention.programme.save()
        self.assertTrue(self.convention.programme.is_residence())

        form_steps = ConventionFormSteps(
            convention=self.convention, request=self.request
        )

        self.assertEqual(
            form_steps.steps,
            [
                bailleur_step,
                programme_step,
                cadastre_step,
                edd_step,
                financement_step,
                foyer_residence_logements_step,
                collectif_step,
                residence_attribution_step,
                foyer_variante_step,
                administration_step,
                commentaires_step,
            ],
        )
