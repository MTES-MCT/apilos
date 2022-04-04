import datetime

from django.test import TestCase
from core.tests import utils_assertions, utils_fixtures
from conventions.models import (
    Convention,
    ConventionHistory,
    ConventionStatut,
    Pret,
    Preteur,
)
from users.models import User
from users.type_models import EmailPreferences


class ConventionModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()
        # bailleur = utils_fixtures.create_bailleur()
        # programme = utils_fixtures.create_programme(bailleur)
        # lot = Lot.objects.create(
        #     programme=programme,
        #     bailleur=bailleur,
        #     financement=Financement.PLUS,
        # )
        # convention = Convention.objects.create(
        #     numero=1,
        #     lot=lot,
        #     programme=programme,
        #     bailleur=bailleur,
        #     financement=Financement.PLUS,
        # )
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
        self.assertTrue(convention.is_instructeur_editable())
        self.assertFalse(convention.is_instruction_ongoing())
        self.assertFalse(convention.is_submitted())
        convention.statut = ConventionStatut.B1_INSTRUCTION
        self.assertFalse(convention.is_bailleur_editable())
        self.assertTrue(convention.is_instructeur_editable())
        self.assertTrue(convention.is_instruction_ongoing())
        self.assertTrue(convention.is_submitted())
        convention.statut = ConventionStatut.B2_CORRECTION
        self.assertTrue(convention.is_bailleur_editable())
        self.assertTrue(convention.is_instructeur_editable())
        self.assertTrue(convention.is_instruction_ongoing())
        self.assertFalse(convention.is_submitted())
        convention.statut = ConventionStatut.C_A_SIGNER
        self.assertFalse(convention.is_bailleur_editable())
        self.assertTrue(convention.is_instructeur_editable())
        self.assertFalse(convention.is_instruction_ongoing())
        self.assertTrue(convention.is_submitted())
        convention.statut = ConventionStatut.D_TRANSMISE
        self.assertFalse(convention.is_bailleur_editable())
        self.assertFalse(convention.is_instructeur_editable())
        self.assertFalse(convention.is_instruction_ongoing())
        self.assertTrue(convention.is_submitted())

    def test_properties(self):
        pret = Pret.objects.first()
        self.assertEqual(pret.get_preteur_display(), pret.p)
        self.assertEqual(pret.autre, pret.a)
        self.assertEqual(pret.date_octroi, pret.do)
        self.assertEqual(pret.numero, pret.n)
        self.assertEqual(pret.duree, pret.d)
        self.assertEqual(pret.montant, pret.m)

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
            statut_convention=ConventionStatut.B1_INSTRUCTION,
            statut_convention_precedent=ConventionStatut.A_PROJET,
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
            statut_convention=ConventionStatut.B1_INSTRUCTION,
            statut_convention_precedent=ConventionStatut.A_PROJET,
            user=sabine,
        ).save()
        self.assertEqual(convention.get_email_instructeur_users(), [sabine.email])

    def test_statut_for_template(self):
        convention = Convention.objects.order_by("uuid").first()
        convention.statut = ConventionStatut.A_PROJET
        self.assertEqual(convention.statut_for_template()["statut"], "1. Projet")
        self.assertEqual(
            convention.statut_for_template()["statut_display"],
            "Création d'un projet de convention",
        )
        self.assertEqual(convention.statut_for_template()["short_statut"], "Projet")
        self.assertEqual(convention.statut_for_template()["key_statut"], "Projet")
        convention.statut = ConventionStatut.B1_INSTRUCTION
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
        convention.statut = ConventionStatut.B2_CORRECTION
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
        convention.statut = ConventionStatut.C_A_SIGNER
        self.assertEqual(convention.statut_for_template()["statut"], "4. A signer")
        self.assertEqual(
            convention.statut_for_template()["statut_display"], "Convention à signer"
        )
        self.assertEqual(convention.statut_for_template()["short_statut"], "A signer")
        self.assertEqual(convention.statut_for_template()["key_statut"], "A_signer")
        convention.statut = ConventionStatut.D_TRANSMISE
        self.assertEqual(convention.statut_for_template()["statut"], "5. Transmise")
        self.assertEqual(
            convention.statut_for_template()["statut_display"], "Convention transmise"
        )
        self.assertEqual(convention.statut_for_template()["short_statut"], "Transmise")
        self.assertEqual(convention.statut_for_template()["key_statut"], "Transmise")

    def test_xlsx(self):
        utils_assertions.assert_xlsx(self, Pret, "financement")
