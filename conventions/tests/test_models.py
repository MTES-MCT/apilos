import datetime

from django.test import TestCase
from conventions.models import Convention, ConventionStatut
from bailleurs.models import Bailleur
from programmes.models import Programme, Lot, Financement

class ConventionModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        bailleur = Bailleur.objects.create(
            nom="3F",
            siret="12345678901234",
            capital_social="SA",
            ville="Marseille",
            dg_nom="Patrick Patoulachi",
            dg_fonction="PDG",
            dg_date_deliberation=datetime.date(2014, 10, 9),
            #            operation_exceptionnelle =
        )
        programme = Programme.objects.create(
            nom="3F",
            bailleur=bailleur,
        )
        lot = Lot.objects.create(
            programme=programme,
            bailleur=bailleur,
            financement=Financement.PLUS,
        )
        Convention.objects.create(
            numero=1,
            lot=lot,
            programme=programme,
            bailleur=bailleur,
            financement=Financement.PLUS,
        )

    def test_object_str(self):
        convention = Convention.objects.get(id=1)
        lot = convention.lot
        programme = convention.programme
        expected_object_name = (f"{programme.nom} - {lot.financement} - " +
            f"{programme.ville} - {programme.nb_logements} lgts")
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
