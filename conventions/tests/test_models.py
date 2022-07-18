import datetime

from django.test import TestCase
from bailleurs.models import TypeBailleur
from core.tests import utils_assertions, utils_fixtures
from conventions.models import (
    Convention,
    ConventionHistory,
    ConventionStatut,
    ConventionType1and2,
    Pret,
    Preteur,
)
from programmes.models import Financement
from users.models import User
from users.type_models import EmailPreferences


class ConventionModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def test_object_str(self):
        convention = Convention.objects.get(numero="0001")
        lot = convention.lot
        type_habitat = lot.get_type_habitat_display()
        programme = convention.programme
        expected_object_name = (
            f"{programme.ville} - {programme.nom} - "
            + f"{lot.nb_logements} lgts - {type_habitat} - {lot.financement}"
        )
        self.assertEqual(str(convention), expected_object_name)

    def test_is_functions(self):
        convention = Convention.objects.get(numero="0001")
        self.assertTrue(convention.is_bailleur_editable())
        self.assertTrue(convention.is_project())
        convention.statut = ConventionStatut.INSTRUCTION
        self.assertFalse(convention.is_bailleur_editable())
        self.assertFalse(convention.is_project())
        convention.statut = ConventionStatut.CORRECTION
        self.assertTrue(convention.is_bailleur_editable())
        self.assertFalse(convention.is_project())
        convention.statut = ConventionStatut.A_SIGNER
        self.assertFalse(convention.is_bailleur_editable())
        self.assertFalse(convention.is_project())
        convention.statut = ConventionStatut.SIGNEE
        self.assertFalse(convention.is_bailleur_editable())
        self.assertFalse(convention.is_project())
        convention.statut = ConventionStatut.RESILIEE
        self.assertFalse(convention.is_bailleur_editable())
        self.assertFalse(convention.is_project())

    def test_display_options(self):
        # pylint: disable=R0915
        convention = Convention.objects.get(numero="0001")
        convention.statut = ConventionStatut.PROJET
        display_options = convention.display_options()
        self.assertFalse(display_options["display_comments"])
        self.assertFalse(display_options["display_comments_summary"])
        self.assertFalse(display_options["display_validation"])
        self.assertFalse(display_options["display_is_validated"])
        self.assertFalse(display_options["display_notification"])
        self.assertFalse(display_options["display_demande_correction"])
        self.assertFalse(display_options["display_demande_instruction"])
        self.assertFalse(display_options["display_redirect_sent"])
        self.assertFalse(display_options["display_progress_bar_2"])
        self.assertFalse(display_options["display_progress_bar_3"])
        self.assertFalse(display_options["display_back_to_instruction"])
        self.assertTrue(display_options["display_progress_bar_1"])
        self.assertTrue(display_options["display_type1and2_editable"])
        convention.statut = ConventionStatut.INSTRUCTION
        display_options = convention.display_options()
        self.assertFalse(display_options["display_is_validated"])
        self.assertFalse(display_options["display_demande_instruction"])
        self.assertFalse(display_options["display_redirect_sent"])
        self.assertFalse(display_options["display_progress_bar_2"])
        self.assertFalse(display_options["display_progress_bar_3"])
        self.assertFalse(display_options["display_back_to_instruction"])
        self.assertTrue(display_options["display_comments"])
        self.assertTrue(display_options["display_comments_summary"])
        self.assertTrue(display_options["display_validation"])
        self.assertTrue(display_options["display_notification"])
        self.assertTrue(display_options["display_demande_correction"])
        self.assertTrue(display_options["display_progress_bar_1"])
        self.assertTrue(display_options["display_type1and2_editable"])
        convention.statut = ConventionStatut.CORRECTION
        display_options = convention.display_options()
        self.assertFalse(display_options["display_is_validated"])
        self.assertFalse(display_options["display_demande_correction"])
        self.assertFalse(display_options["display_redirect_sent"])
        self.assertFalse(display_options["display_progress_bar_2"])
        self.assertFalse(display_options["display_progress_bar_3"])
        self.assertFalse(display_options["display_back_to_instruction"])
        self.assertTrue(display_options["display_comments"])
        self.assertTrue(display_options["display_comments_summary"])
        self.assertTrue(display_options["display_validation"])
        self.assertTrue(display_options["display_notification"])
        self.assertTrue(display_options["display_demande_instruction"])
        self.assertTrue(display_options["display_progress_bar_1"])
        self.assertTrue(display_options["display_type1and2_editable"])
        convention.statut = ConventionStatut.A_SIGNER
        display_options = convention.display_options()
        self.assertFalse(display_options["display_comments_summary"])
        self.assertFalse(display_options["display_validation"])
        self.assertFalse(display_options["display_notification"])
        self.assertFalse(display_options["display_demande_correction"])
        self.assertFalse(display_options["display_demande_instruction"])
        self.assertFalse(display_options["display_progress_bar_1"])
        self.assertFalse(display_options["display_progress_bar_3"])
        self.assertFalse(display_options["display_type1and2_editable"])
        self.assertTrue(display_options["display_comments"])
        self.assertTrue(display_options["display_is_validated"])
        self.assertTrue(display_options["display_redirect_sent"])
        self.assertTrue(display_options["display_progress_bar_2"])
        self.assertTrue(display_options["display_back_to_instruction"])
        convention.statut = ConventionStatut.SIGNEE
        display_options = convention.display_options()
        self.assertFalse(display_options["display_comments_summary"])
        self.assertFalse(display_options["display_validation"])
        self.assertFalse(display_options["display_notification"])
        self.assertFalse(display_options["display_demande_correction"])
        self.assertFalse(display_options["display_demande_instruction"])
        self.assertFalse(display_options["display_progress_bar_1"])
        self.assertFalse(display_options["display_progress_bar_2"])
        self.assertFalse(display_options["display_type1and2_editable"])
        self.assertFalse(display_options["display_back_to_instruction"])
        self.assertTrue(display_options["display_comments"])
        self.assertTrue(display_options["display_is_validated"])
        self.assertTrue(display_options["display_redirect_sent"])
        self.assertTrue(display_options["display_progress_bar_3"])
        convention.statut = ConventionStatut.RESILIEE
        display_options = convention.display_options()
        self.assertFalse(display_options["display_comments"])
        self.assertFalse(display_options["display_comments_summary"])
        self.assertFalse(display_options["display_validation"])
        self.assertFalse(display_options["display_notification"])
        self.assertFalse(display_options["display_demande_correction"])
        self.assertFalse(display_options["display_demande_instruction"])
        self.assertFalse(display_options["display_progress_bar_1"])
        self.assertFalse(display_options["display_progress_bar_2"])
        self.assertFalse(display_options["display_progress_bar_3"])
        self.assertFalse(display_options["display_type1and2_editable"])
        self.assertFalse(display_options["display_back_to_instruction"])
        self.assertFalse(display_options["display_redirect_sent"])
        self.assertTrue(display_options["display_is_validated"])

    def test_get_email_bailleur_users(self):
        convention = Convention.objects.get(numero="0001")
        raph = User.objects.get(username="raph")
        self.assertEqual(convention.get_email_bailleur_users(), [raph.email])
        raph.preferences_email = EmailPreferences.AUCUN
        raph.save()
        self.assertEqual(convention.get_email_bailleur_users(), [])
        raph.preferences_email = EmailPreferences.PARTIEL
        raph.save()
        self.assertEqual(convention.get_email_bailleur_users(), [])
        ConventionHistory.objects.create(
            bailleur=convention.bailleur,
            convention=convention,
            statut_convention=ConventionStatut.INSTRUCTION,
            statut_convention_precedent=ConventionStatut.PROJET,
            user=raph,
        ).save()
        self.assertEqual(convention.get_email_bailleur_users(), [raph.email])

    def test_get_email_inctructeur_users(self):
        convention = Convention.objects.get(numero="0001")
        sabine = User.objects.get(username="sabine")
        self.assertEqual(convention.get_email_instructeur_users(), [sabine.email])
        sabine.preferences_email = EmailPreferences.AUCUN
        sabine.save()
        self.assertEqual(convention.get_email_instructeur_users(), [])
        sabine.preferences_email = EmailPreferences.PARTIEL
        sabine.save()
        self.assertEqual(convention.get_email_instructeur_users(), [])
        self.assertEqual(
            convention.get_email_instructeur_users(include_partial=True), [sabine.email]
        )
        ConventionHistory.objects.create(
            bailleur=convention.bailleur,
            convention=convention,
            statut_convention=ConventionStatut.INSTRUCTION,
            statut_convention_precedent=ConventionStatut.PROJET,
            user=sabine,
        ).save()
        self.assertEqual(convention.get_email_instructeur_users(), [sabine.email])

    def test_statut_for_template(self):
        convention = Convention.objects.order_by("uuid").first()
        convention.statut = ConventionStatut.PROJET
        self.assertEqual(convention.statut_for_template()["statut"], "1. Projet")
        self.assertEqual(
            convention.statut_for_template()["statut_display"],
            "Création d'un projet de convention",
        )
        self.assertEqual(
            convention.statut_for_template()["short_statut"], "Projet (Brouillon)"
        )
        self.assertEqual(convention.statut_for_template()["key_statut"], "Projet")
        convention.statut = ConventionStatut.INSTRUCTION
        self.assertEqual(
            convention.statut_for_template()["statut"], "2. Instruction requise"
        )
        self.assertEqual(
            convention.statut_for_template()["statut_display"],
            "Projet de convention soumis à l'instruction",
        )
        self.assertEqual(
            convention.statut_for_template()["short_statut"], "Instruction requise"
        )
        self.assertEqual(
            convention.statut_for_template()["key_statut"], "Instruction_requise"
        )
        convention.statut = ConventionStatut.CORRECTION
        self.assertEqual(
            convention.statut_for_template()["statut"], "3. Corrections requises"
        )
        self.assertEqual(
            convention.statut_for_template()["statut_display"],
            "Projet de convention à modifier par le bailleur",
        )
        self.assertEqual(
            convention.statut_for_template()["short_statut"], "Corrections requises"
        )
        self.assertEqual(
            convention.statut_for_template()["key_statut"], "Corrections_requises"
        )
        convention.statut = ConventionStatut.A_SIGNER
        self.assertEqual(convention.statut_for_template()["statut"], "4. A signer")
        self.assertEqual(
            convention.statut_for_template()["statut_display"], "Convention à signer"
        )
        self.assertEqual(convention.statut_for_template()["short_statut"], "A signer")
        self.assertEqual(convention.statut_for_template()["key_statut"], "A_signer")
        convention.statut = ConventionStatut.SIGNEE
        self.assertEqual(convention.statut_for_template()["statut"], "5. Signée")
        self.assertEqual(
            convention.statut_for_template()["statut_display"], "Convention signée"
        )
        self.assertEqual(convention.statut_for_template()["short_statut"], "Signée")
        self.assertEqual(convention.statut_for_template()["key_statut"], "Signee")

    def test_mixity_option(self):
        convention = Convention.objects.order_by("uuid").first()
        convention.financement = Financement.PLUS
        self.assertTrue(convention.mixity_option())
        for k, _ in Financement.choices:
            if k != Financement.PLUS:
                convention.financement = k
                self.assertFalse(convention.mixity_option())

    def test_type1and2_configuration_not_needed(self):
        convention = Convention.objects.order_by("uuid").first()
        for type_bailleur in [
            TypeBailleur.OFFICE_PUBLIC_HLM,
            TypeBailleur.SA_HLM_ESH,
            TypeBailleur.COOPERATIVE_HLM_SCIC,
            TypeBailleur.SEM_EPL,
        ]:
            convention.bailleur.type_bailleur = type_bailleur
            for type1andtype2 in [
                ConventionType1and2.TYPE1,
                ConventionType1and2.TYPE2,
                None,
            ]:
                convention.type1and2 = type1andtype2
                self.assertTrue(convention.type1and2_configuration_not_needed())
        for k, _ in TypeBailleur.choices:
            if k not in [
                TypeBailleur.OFFICE_PUBLIC_HLM,
                TypeBailleur.SA_HLM_ESH,
                TypeBailleur.COOPERATIVE_HLM_SCIC,
                TypeBailleur.SEM_EPL,
            ]:
                convention.bailleur.type_bailleur = k
                convention.type1and2 = None
                self.assertFalse(convention.type1and2_configuration_not_needed())
                for type1andtype2 in [
                    ConventionType1and2.TYPE1,
                    ConventionType1and2.TYPE2,
                ]:
                    convention.type1and2 = type1andtype2
                    self.assertTrue(convention.type1and2_configuration_not_needed())

    def test_display_not_validated_status(self):
        convention = Convention.objects.order_by("uuid").first()
        convention.statut = ConventionStatut.PROJET
        self.assertEqual(
            convention.display_not_validated_status(), "Projet de convention"
        )
        convention.statut = ConventionStatut.INSTRUCTION
        self.assertEqual(
            convention.display_not_validated_status(),
            "Convention en cours d'instruction",
        )
        convention.statut = ConventionStatut.CORRECTION
        self.assertEqual(
            convention.display_not_validated_status(),
            "Convention en cours d'instruction",
        )
        convention.statut = ConventionStatut.A_SIGNER
        self.assertEqual(convention.display_not_validated_status(), "")
        convention.statut = ConventionStatut.SIGNEE
        self.assertEqual(convention.display_not_validated_status(), "")

    def test_xlsx(self):
        utils_assertions.assert_xlsx(self, Pret, "financement")


class PretModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()
        convention = Convention.objects.get(numero="0001")
        Pret.objects.create(
            convention=convention,
            bailleur=convention.bailleur,
            preteur=Preteur.CDCF,
            date_octroi=datetime.datetime.today(),
            autre="test autre",
            numero="mon numero",
            duree=50,
            montant=123456.789,
        )

    def test_p_full(self):
        pret = Pret.objects.first()
        pret.preteur = Preteur.CDCF
        self.assertEqual(
            pret.p_full(), "Caisse de Dépôts et Consignation pour le foncier"
        )
        pret.preteur = Preteur.CDCL
        self.assertEqual(
            pret.p_full(), "Caisse de Dépôts et Consignation pour le logement"
        )
        pret.preteur = Preteur.AUTRE
        self.assertEqual(pret.p_full(), "Autre")
        pret.preteur = Preteur.ETAT
        self.assertEqual(pret.p_full(), "Etat")
        pret.preteur = Preteur.REGION
        self.assertEqual(pret.p_full(), "Région")

    def test_properties(self):
        pret = Pret.objects.first()
        self.assertEqual(pret.get_preteur_display(), pret.p)
        self.assertEqual(pret.autre, pret.a)
        self.assertEqual(pret.date_octroi, pret.do)
        self.assertEqual(pret.numero, pret.n)
        self.assertEqual(pret.duree, pret.d)
        self.assertEqual(pret.montant, pret.m)

    def test_preteur_display(self):
        pret = Pret.objects.first()

        for k, _ in Preteur.choices:
            if k != Preteur.AUTRE:
                pret.preteur = k
                self.assertEqual(pret.p_full(), pret.preteur_display())
        pret.preteur = Preteur.AUTRE
        pret.autre = "n'importe quoi"
        self.assertEqual(pret.preteur_display(), "n'importe quoi")
