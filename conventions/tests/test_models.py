import datetime

from django.test import TestCase
from core.tests import utils
from conventions.models import Convention, ConventionStatut, Pret, Preteur
from programmes.models import Lot, Financement

class ConventionModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        bailleur = utils.create_bailleur()
        programme = utils.create_programme(bailleur)
        lot = Lot.objects.create(
            programme=programme,
            bailleur=bailleur,
            financement=Financement.PLUS,
        )
        convention = Convention.objects.create(
            numero=1,
            lot=lot,
            programme=programme,
            bailleur=bailleur,
            financement=Financement.PLUS,
        )
        Pret.objects.create(
            convention = convention,
            bailleur = bailleur,
            preteur = Preteur.CDCF,
            date_octroi = datetime.datetime.today(),
            autre = "test autre",
            numero = "mon numero",
            duree = 50,
            montant = 123456.789
        )


    def test_object_str(self):
        convention = Convention.objects.get(id=1)
        lot = convention.lot
        programme = convention.programme
        expected_object_name = (f"{programme.nom} - {lot.financement} - " +
            f"{programme.ville} - {lot.nb_logements} lgts")
        self.assertEqual(str(convention), expected_object_name)

    def test_is_functions(self):
        convention = Convention.objects.get(id=1)
        self.assertTrue(convention.is_bailleur_editable())
        self.assertTrue(convention.is_instructeur_editable())
        self.assertFalse(convention.is_submitted())
        convention.statut = ConventionStatut.INSTRUCTION
        self.assertFalse(convention.is_bailleur_editable())
        self.assertTrue(convention.is_instructeur_editable())
        self.assertTrue(convention.is_submitted())
        convention.statut = ConventionStatut.CORRECTION
        self.assertTrue(convention.is_bailleur_editable())
        self.assertTrue(convention.is_instructeur_editable())
        self.assertFalse(convention.is_submitted())
        convention.statut = ConventionStatut.VALIDE
        self.assertFalse(convention.is_bailleur_editable())
        self.assertTrue(convention.is_instructeur_editable())
        self.assertTrue(convention.is_submitted())
        convention.statut = ConventionStatut.CLOS
        self.assertFalse(convention.is_bailleur_editable())
        self.assertFalse(convention.is_instructeur_editable())
        self.assertTrue(convention.is_submitted())


    def test_properties(self):
        pret = Pret.objects.first()
        self.assertEqual(pret.preteur, pret.p)
        self.assertEqual(pret.autre, pret.a)
        self.assertEqual(pret.date_octroi, pret.do)
        self.assertEqual(pret.numero, pret.n)
        self.assertEqual(pret.duree, pret.d)
        self.assertEqual(pret.montant, pret.m)

    def test_p_full(self):
        pret = Pret.objects.first()
        pret.preteur = Preteur.CDCF
        self.assertEqual(pret.p_full(), 'Caisse des dépôts et des consignations froncière')
        pret.preteur = Preteur.CDCL
        self.assertEqual(pret.p_full(), 'Caisse des dépôts et des consignations locative')
        pret.preteur = Preteur.AUTRE
        self.assertEqual(pret.p_full(), 'Autre')
        pret.preteur = Preteur.ETAT
        self.assertEqual(pret.p_full(), 'Etat')
        pret.preteur = Preteur.REGION
        self.assertEqual(pret.p_full(), 'Région')

    def test_xlsx(self):
        utils.assert_xlsx(self, Pret, 'prets')
