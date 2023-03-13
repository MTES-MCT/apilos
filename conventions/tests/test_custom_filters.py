from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase, override_settings
from bailleurs.models import SousNatureBailleur
from conventions.views import ConventionFormSteps
from conventions.models import (
    Convention,
    ConventionStatut,
    ConventionType1and2,
)
from conventions.templatetags import custom_filters
from programmes.models import ActiveNatureLogement
from users.models import GroupProfile, User


class CustomFiltersTest(TestCase):
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
        self.convention = Convention.objects.get(numero="0001")
        get_response = mock.MagicMock()
        self.request = RequestFactory().get("/conventions")
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_is_bailleur_is_instructeur(self):
        self.request.session["currently"] = GroupProfile.STAFF
        self.assertTrue(custom_filters.is_bailleur(self.request))
        self.assertTrue(custom_filters.is_instructeur(self.request))
        for profile in [
            GroupProfile.BAILLEUR,
            GroupProfile.SIAP_MO_PERS_MORALE,
            GroupProfile.SIAP_MO_PERS_PHYS,
        ]:
            self.request.session["currently"] = profile
            self.assertTrue(custom_filters.is_bailleur(self.request))
            self.assertFalse(custom_filters.is_instructeur(self.request))
        for profile in [
            GroupProfile.INSTRUCTEUR,
            GroupProfile.SIAP_SER_GEST,
            GroupProfile.SIAP_ADM_CENTRALE,
        ]:
            self.request.session["currently"] = profile
            self.assertFalse(custom_filters.is_bailleur(self.request))
            self.assertTrue(custom_filters.is_instructeur(self.request))

    def test_display_comments(self):
        self.convention.statut = ConventionStatut.PROJET
        self.assertFalse(custom_filters.display_comments(self.convention))

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.assertTrue(custom_filters.display_comments(self.convention))

        self.convention.statut = ConventionStatut.CORRECTION
        self.assertTrue(custom_filters.display_comments(self.convention))

        self.convention.statut = ConventionStatut.A_SIGNER
        self.assertTrue(custom_filters.display_comments(self.convention))

        self.convention.statut = ConventionStatut.RESILIEE
        self.assertFalse(custom_filters.display_comments(self.convention))

    def test_display_comments_summary(self):
        self.convention.statut = ConventionStatut.PROJET
        self.assertFalse(custom_filters.display_comments_summary(self.convention))

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.assertTrue(custom_filters.display_comments_summary(self.convention))

        self.convention.statut = ConventionStatut.CORRECTION
        self.assertTrue(custom_filters.display_comments_summary(self.convention))

        self.convention.statut = ConventionStatut.A_SIGNER
        self.assertFalse(custom_filters.display_comments_summary(self.convention))

        self.convention.statut = ConventionStatut.SIGNEE
        self.assertFalse(custom_filters.display_comments_summary(self.convention))

        self.convention.statut = ConventionStatut.RESILIEE
        self.assertFalse(custom_filters.display_comments_summary(self.convention))

    def test_display_is_validated(self):

        self.convention.statut = ConventionStatut.PROJET
        self.assertFalse(custom_filters.display_is_validated(self.convention))

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.assertFalse(custom_filters.display_is_validated(self.convention))

        self.convention.statut = ConventionStatut.CORRECTION
        self.assertFalse(custom_filters.display_is_validated(self.convention))

        self.convention.statut = ConventionStatut.A_SIGNER
        self.assertTrue(custom_filters.display_is_validated(self.convention))

        self.convention.statut = ConventionStatut.SIGNEE
        self.assertTrue(custom_filters.display_is_validated(self.convention))

        self.convention.statut = ConventionStatut.RESILIEE
        self.assertTrue(custom_filters.display_is_validated(self.convention))

    def test_display_demande_correction(self):
        self.convention.statut = ConventionStatut.PROJET
        self.assertFalse(custom_filters.display_demande_correction(self.convention))

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.assertTrue(custom_filters.display_demande_correction(self.convention))

        self.convention.statut = ConventionStatut.CORRECTION
        self.assertFalse(custom_filters.display_demande_correction(self.convention))

        self.convention.statut = ConventionStatut.A_SIGNER
        self.assertFalse(custom_filters.display_demande_correction(self.convention))

        self.convention.statut = ConventionStatut.SIGNEE
        self.assertFalse(custom_filters.display_demande_correction(self.convention))

        self.convention.statut = ConventionStatut.RESILIEE
        self.assertFalse(custom_filters.display_demande_correction(self.convention))

    def test_display_demande_instruction(self):
        self.convention.statut = ConventionStatut.PROJET
        self.assertFalse(custom_filters.display_demande_instruction(self.convention))

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.assertFalse(custom_filters.display_demande_instruction(self.convention))

        self.convention.statut = ConventionStatut.CORRECTION
        self.assertTrue(custom_filters.display_demande_instruction(self.convention))

        self.convention.statut = ConventionStatut.A_SIGNER
        self.assertFalse(custom_filters.display_demande_instruction(self.convention))

        self.convention.statut = ConventionStatut.SIGNEE
        self.assertFalse(custom_filters.display_demande_instruction(self.convention))

        self.convention.statut = ConventionStatut.RESILIEE
        self.assertFalse(custom_filters.display_demande_instruction(self.convention))

    def test_display_redirect_sent(self):
        self.convention.statut = ConventionStatut.PROJET
        self.assertFalse(custom_filters.display_redirect_sent(self.convention))

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.assertFalse(custom_filters.display_redirect_sent(self.convention))

        self.convention.statut = ConventionStatut.CORRECTION
        self.assertFalse(custom_filters.display_redirect_sent(self.convention))

        self.convention.statut = ConventionStatut.A_SIGNER
        self.assertTrue(custom_filters.display_redirect_sent(self.convention))

        self.convention.statut = ConventionStatut.SIGNEE
        self.assertFalse(custom_filters.display_redirect_sent(self.convention))

        self.convention.statut = ConventionStatut.RESILIEE
        self.assertFalse(custom_filters.display_redirect_sent(self.convention))

    def test_display_redirect_project_without_cerbere(self):
        for statut in ConventionStatut:
            self.convention.statut = statut
            self.assertFalse(custom_filters.display_redirect_project(self.convention))

    @override_settings(CERBERE_AUTH="htpps://cerbere.com")
    def test_display_redirect_project_with_cerbere(self):
        self.convention.statut = ConventionStatut.PROJET
        self.assertTrue(custom_filters.display_redirect_project(self.convention))

        for statut in [
            ConventionStatut.INSTRUCTION,
            ConventionStatut.CORRECTION,
            ConventionStatut.A_SIGNER,
            ConventionStatut.SIGNEE,
            ConventionStatut.RESILIEE,
        ]:
            self.convention.statut = statut
            self.assertFalse(custom_filters.display_redirect_project(self.convention))

    def test_display_redirect_post_action(self):

        self.convention.statut = ConventionStatut.PROJET
        self.assertFalse(custom_filters.display_redirect_post_action(self.convention))

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.assertFalse(custom_filters.display_redirect_post_action(self.convention))

        self.convention.statut = ConventionStatut.CORRECTION
        self.assertFalse(custom_filters.display_redirect_post_action(self.convention))

        self.convention.statut = ConventionStatut.A_SIGNER
        self.assertFalse(custom_filters.display_redirect_post_action(self.convention))

        self.convention.statut = ConventionStatut.SIGNEE
        self.assertTrue(custom_filters.display_redirect_post_action(self.convention))

        self.convention.statut = ConventionStatut.RESILIEE
        self.assertFalse(custom_filters.display_redirect_post_action(self.convention))

    def test_display_convention_form_progressbar(self):

        self.convention.statut = ConventionStatut.PROJET
        self.assertTrue(
            custom_filters.display_convention_form_progressbar(self.convention)
        )

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.assertTrue(
            custom_filters.display_convention_form_progressbar(self.convention)
        )

        self.convention.statut = ConventionStatut.CORRECTION
        self.assertTrue(
            custom_filters.display_convention_form_progressbar(self.convention)
        )

        self.convention.statut = ConventionStatut.SIGNEE
        self.assertFalse(
            custom_filters.display_convention_form_progressbar(self.convention)
        )

        self.convention.statut = ConventionStatut.RESILIEE
        self.assertFalse(
            custom_filters.display_convention_form_progressbar(self.convention)
        )

    def test_display_type1and2_editable(self):
        self.convention.statut = ConventionStatut.PROJET
        self.assertTrue(custom_filters.display_type1and2_editable(self.convention))

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.assertTrue(custom_filters.display_type1and2_editable(self.convention))

        self.convention.statut = ConventionStatut.CORRECTION
        self.assertTrue(custom_filters.display_type1and2_editable(self.convention))

        self.convention.statut = ConventionStatut.A_SIGNER
        self.assertFalse(custom_filters.display_type1and2_editable(self.convention))

        self.convention.statut = ConventionStatut.SIGNEE
        self.assertFalse(custom_filters.display_type1and2_editable(self.convention))

        self.convention.statut = ConventionStatut.RESILIEE
        self.assertFalse(custom_filters.display_type1and2_editable(self.convention))

    def test_display_validation(self):
        self.convention.statut = ConventionStatut.PROJET
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )
        self.convention.cree_par = User.objects.get(username="fix")
        self.assertTrue(
            custom_filters.display_validation(self.convention, self.request)
        )
        self.convention.cree_par = User.objects.get(username="raph")
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertTrue(
            custom_filters.display_validation(self.convention, self.request)
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )

        self.convention.statut = ConventionStatut.CORRECTION
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertTrue(
            custom_filters.display_validation(self.convention, self.request)
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )

        self.convention.statut = ConventionStatut.A_SIGNER
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )

        self.convention.statut = ConventionStatut.SIGNEE
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )

        self.convention.statut = ConventionStatut.RESILIEE
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_validation(self.convention, self.request)
        )

    def test_display_notification_instructeur_to_bailleur(self):
        self.convention.statut = ConventionStatut.PROJET
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertTrue(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )

        self.convention.statut = ConventionStatut.CORRECTION
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertTrue(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )

        self.convention.statut = ConventionStatut.A_SIGNER
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )

        self.convention.statut = ConventionStatut.SIGNEE
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )

        self.convention.statut = ConventionStatut.RESILIEE
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_notification_instructeur_to_bailleur(
                self.convention, self.request
            )
        )

    def test_display_notification_bailleur_to_instructeur(self):
        self.convention.statut = ConventionStatut.PROJET
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertTrue(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )

        self.convention.statut = ConventionStatut.CORRECTION
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertTrue(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )

        self.convention.statut = ConventionStatut.A_SIGNER
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )

        self.convention.statut = ConventionStatut.SIGNEE
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )

        self.convention.statut = ConventionStatut.RESILIEE
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_notification_bailleur_to_instructeur(
                self.convention,
                self.request,
            )
        )

    def test_display_back_to_instruction(self):
        self.convention.statut = ConventionStatut.PROJET
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )

        self.convention.statut = ConventionStatut.CORRECTION
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )

        self.convention.statut = ConventionStatut.A_SIGNER
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertTrue(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )

        self.convention.statut = ConventionStatut.SIGNEE
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertTrue(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )

        self.convention.statut = ConventionStatut.RESILIEE
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertFalse(
            custom_filters.display_back_to_instruction(
                self.convention,
                self.request,
            )
        )

    def test_display_submit_convention(self):
        self.convention.statut = ConventionStatut.PROJET
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.assertFalse(
            custom_filters.display_submit_convention(self.convention, self.request)
        )
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.assertTrue(
            custom_filters.display_submit_convention(self.convention, self.request)
        )

        for convention_statut in [
            ConventionStatut.INSTRUCTION,
            ConventionStatut.CORRECTION,
            ConventionStatut.A_SIGNER,
            ConventionStatut.RESILIEE,
        ]:
            self.convention.statut = convention_statut
            for group_profile in [GroupProfile.INSTRUCTEUR, GroupProfile.BAILLEUR]:
                self.request.session["currently"] = group_profile
                self.assertFalse(
                    custom_filters.display_submit_convention(
                        self.convention, self.request
                    )
                )

    def test_display_delete_convention(self):

        self.convention.statut = ConventionStatut.PROJET
        self.assertTrue(custom_filters.display_delete_convention(self.convention))

        self.convention.statut = ConventionStatut.INSTRUCTION
        self.assertTrue(custom_filters.display_delete_convention(self.convention))

        self.convention.statut = ConventionStatut.CORRECTION
        self.assertTrue(custom_filters.display_delete_convention(self.convention))

        self.convention.statut = ConventionStatut.A_SIGNER
        self.assertFalse(custom_filters.display_delete_convention(self.convention))

        self.convention.statut = ConventionStatut.SIGNEE
        self.assertFalse(custom_filters.display_delete_convention(self.convention))

        self.convention.statut = ConventionStatut.RESILIEE
        self.assertFalse(custom_filters.display_delete_convention(self.convention))

    def test_display_create_avenant(self):
        self.assertTrue(custom_filters.display_create_avenant(self.convention))
        Convention.objects.create(
            statut=ConventionStatut.A_SIGNER,
            parent=self.convention,
            lot=self.convention.lot,
            programme=self.convention.programme,
        ).save()
        self.assertTrue(custom_filters.display_create_avenant(self.convention))
        Convention.objects.create(
            statut=ConventionStatut.SIGNEE,
            parent=self.convention,
            lot=self.convention.lot,
            programme=self.convention.programme,
        ).save()
        self.assertTrue(custom_filters.display_create_avenant(self.convention))
        Convention.objects.create(
            statut=ConventionStatut.RESILIEE,
            parent=self.convention,
            lot=self.convention.lot,
            programme=self.convention.programme,
        ).save()
        self.assertTrue(custom_filters.display_create_avenant(self.convention))
        ongoing_avenant = Convention.objects.create(
            statut=ConventionStatut.PROJET,
            parent=self.convention,
            lot=self.convention.lot,
            programme=self.convention.programme,
        )
        ongoing_avenant.save()
        self.assertFalse(custom_filters.display_create_avenant(self.convention))
        ongoing_avenant.statut = ConventionStatut.INSTRUCTION
        ongoing_avenant.save()
        self.assertFalse(custom_filters.display_create_avenant(self.convention))
        ongoing_avenant.statut = ConventionStatut.CORRECTION
        ongoing_avenant.save()
        self.assertFalse(custom_filters.display_create_avenant(self.convention))
        ongoing_avenant.statut = ConventionStatut.A_SIGNER
        ongoing_avenant.save()
        self.assertTrue(custom_filters.display_create_avenant(self.convention))

    def test_display_type1and2(self):
        for sous_nature_bailleur in [
            SousNatureBailleur.OFFICE_PUBLIC_HLM,
            SousNatureBailleur.SA_HLM_ESH,
            SousNatureBailleur.COOPERATIVE_HLM_SCIC,
            SousNatureBailleur.SEM_EPL,
        ]:
            bailleur = self.convention.programme.bailleur
            bailleur.sous_nature_bailleur = sous_nature_bailleur
            bailleur.save()
            for type1andtype2 in [
                ConventionType1and2.TYPE1,
                ConventionType1and2.TYPE2,
                None,
            ]:
                self.convention.type1and2 = type1andtype2
                self.assertFalse(custom_filters.display_type1and2(self.convention))

        for sous_nature_bailleur in [
            SousNatureBailleur.ASSOCIATIONS,
            SousNatureBailleur.COMMERCIALES,
            SousNatureBailleur.COMMUNE,
            SousNatureBailleur.CROUS,
            SousNatureBailleur.DEPARTEMENT,
            SousNatureBailleur.DRE_DDE_CETE_AC_PREF,
            SousNatureBailleur.EPCI,
            SousNatureBailleur.ETC_PUBLIQUE_LOCAL,
            SousNatureBailleur.ETS_HOSTIPATIERS_PRIVES,
            SousNatureBailleur.FONDATION,
            SousNatureBailleur.FONDATION_HLM,
            SousNatureBailleur.FRONCIERE_LOGEMENT,
            SousNatureBailleur.GIP,
            SousNatureBailleur.MUTUELLE,
            SousNatureBailleur.NONRENSEIGNE,
            SousNatureBailleur.PACT_ARIM,
            SousNatureBailleur.PARTICULIERS,
            SousNatureBailleur.SACI_CAP,
            SousNatureBailleur.UES,
        ]:
            bailleur = self.convention.programme.bailleur
            bailleur.sous_nature_bailleur = sous_nature_bailleur
            bailleur.save()

            for nature_logement, _ in ActiveNatureLogement.choices:
                self.convention.programme.nature_logement = nature_logement

                for type1andtype2 in [
                    ConventionType1and2.TYPE1,
                    ConventionType1and2.TYPE2,
                    None,
                ]:
                    if nature_logement in [
                        ActiveNatureLogement.LOGEMENTSORDINAIRES,
                        ActiveNatureLogement.RESIDENCEUNIVERSITAIRE,
                    ]:
                        self.assertTrue(
                            custom_filters.display_type1and2(self.convention)
                        )
                    else:
                        self.assertFalse(
                            custom_filters.display_type1and2(self.convention)
                        )

        avenant = Convention.objects.create(
            statut=ConventionStatut.SIGNEE,
            parent=self.convention,
            lot=self.convention.lot,
            programme=self.convention.programme,
        )
        avenant.type1and2 = None
        avenant.programme.bailleur.sous_nature_bailleur = (
            SousNatureBailleur.ASSOCIATIONS
        )
        for sous_nature_bailleur, _ in SousNatureBailleur.choices:
            avenant.programme.bailleur.sous_nature_bailleur = sous_nature_bailleur
            for type1andtype2 in [
                ConventionType1and2.TYPE1,
                ConventionType1and2.TYPE2,
                None,
            ]:
                self.assertFalse(custom_filters.display_type1and2(avenant))

    def test_display_deactivated_because_type1and2_config_is_needed(self):
        for sous_nature_bailleur in [
            SousNatureBailleur.OFFICE_PUBLIC_HLM,
            SousNatureBailleur.SA_HLM_ESH,
            SousNatureBailleur.COOPERATIVE_HLM_SCIC,
            SousNatureBailleur.SEM_EPL,
        ]:
            bailleur = self.convention.programme.bailleur
            bailleur.sous_nature_bailleur = sous_nature_bailleur
            bailleur.save()
            for type1andtype2 in [
                ConventionType1and2.TYPE1,
                ConventionType1and2.TYPE2,
                None,
            ]:
                self.convention.type1and2 = type1andtype2
                self.assertFalse(
                    custom_filters.display_deactivated_because_type1and2_config_is_needed(
                        self.convention
                    )
                )

        for sous_nature_bailleur in [
            SousNatureBailleur.ASSOCIATIONS,
            SousNatureBailleur.COMMERCIALES,
            SousNatureBailleur.COMMUNE,
            SousNatureBailleur.CROUS,
            SousNatureBailleur.DEPARTEMENT,
            SousNatureBailleur.DRE_DDE_CETE_AC_PREF,
            SousNatureBailleur.EPCI,
            SousNatureBailleur.ETC_PUBLIQUE_LOCAL,
            SousNatureBailleur.ETS_HOSTIPATIERS_PRIVES,
            SousNatureBailleur.FONDATION,
            SousNatureBailleur.FONDATION_HLM,
            SousNatureBailleur.FRONCIERE_LOGEMENT,
            SousNatureBailleur.GIP,
            SousNatureBailleur.MUTUELLE,
            SousNatureBailleur.NONRENSEIGNE,
            SousNatureBailleur.PACT_ARIM,
            SousNatureBailleur.PARTICULIERS,
            SousNatureBailleur.SACI_CAP,
            SousNatureBailleur.UES,
        ]:
            bailleur = self.convention.programme.bailleur
            bailleur.sous_nature_bailleur = sous_nature_bailleur
            bailleur.save()

            for nature_logement, _ in ActiveNatureLogement.choices:
                self.convention.programme.nature_logement = nature_logement

                for type1andtype2 in [
                    ConventionType1and2.TYPE1,
                    ConventionType1and2.TYPE2,
                ]:
                    self.convention.type1and2 = type1andtype2
                    self.assertFalse(
                        custom_filters.display_deactivated_because_type1and2_config_is_needed(
                            self.convention
                        )
                    )
                self.convention.type1and2 = None
                if nature_logement in [
                    ActiveNatureLogement.LOGEMENTSORDINAIRES,
                    ActiveNatureLogement.RESIDENCEUNIVERSITAIRE,
                ]:
                    self.assertTrue(
                        custom_filters.display_deactivated_because_type1and2_config_is_needed(
                            self.convention
                        )
                    )
                else:
                    self.assertFalse(
                        custom_filters.display_deactivated_because_type1and2_config_is_needed(
                            self.convention
                        )
                    )

        avenant = Convention.objects.create(
            statut=ConventionStatut.SIGNEE,
            parent=self.convention,
            lot=self.convention.lot,
            programme=self.convention.programme,
        )
        avenant.type1and2 = None
        avenant.programme.bailleur.sous_nature_bailleur = (
            SousNatureBailleur.ASSOCIATIONS
        )
        for sous_nature_bailleur, _ in SousNatureBailleur.choices:
            avenant.programme.bailleur.sous_nature_bailleur = sous_nature_bailleur
            for type1andtype2 in [
                ConventionType1and2.TYPE1,
                ConventionType1and2.TYPE2,
                None,
            ]:
                self.assertFalse(
                    custom_filters.display_deactivated_because_type1and2_config_is_needed(
                        avenant
                    )
                )

    def is_a_step(self):
        self.convention.programme.nature_logement = (
            ActiveNatureLogement.LOGEMENTSORDINAIRES
        )
        convention_form_steps = ConventionFormSteps(convention=self.convention)
        self.assertTrue(custom_filters.is_a_step(convention_form_steps, "Bailleur"))
        self.assertTrue(
            custom_filters.is_a_step(convention_form_steps, "Stationnement")
        )
        self.assertFalse(custom_filters.is_a_step(convention_form_steps, "Attribution"))
        self.convention.programme.nature_logement = ActiveNatureLogement.AUTRE
        self.assertTrue(custom_filters.is_a_step(convention_form_steps, "Bailleur"))
        self.assertFalse(
            custom_filters.is_a_step(convention_form_steps, "Stationnement")
        )
        self.assertTrue(custom_filters.is_a_step(convention_form_steps, "Attribution"))

    def test_get_text_as_list(self):
        self.assertEqual(
            custom_filters.get_text_as_list(
                "First line\r\nSecond line\r\nThird line\r\n\r\n "
            ),
            ["First line", "Second line", "Third line"],
        )
        self.assertEqual(
            custom_filters.get_text_as_list(
                "* First line\r\n - Second line - \r\nThird line\r\n\r\n "
            ),
            ["First line", "Second line", "Third line"],
        )
