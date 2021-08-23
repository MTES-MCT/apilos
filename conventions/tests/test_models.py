from django.test import TestCase
from conventions.models import Convention
from bailleurs.models import Bailleur
from programmes.models import Programme, Lot, Financement
import datetime

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
            financement= Financement.PLUS,
        )
        Convention.objects.create(
            numero=1,
            lot=lot,
            programme=programme,
            bailleur=bailleur,
            financement= Financement.PLUS,
        )

    def test_object_str(self):
        convention = Convention.objects.get(id=1)
        lot = convention.lot
        programme = convention.programme
        expected_object_name = f"{programme.nom} - {lot.financement} - {programme.ville} - {programme.nb_logements} lgts"
        self.assertEqual(str(convention), expected_object_name)
