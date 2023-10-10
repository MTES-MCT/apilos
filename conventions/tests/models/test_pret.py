import datetime

from django.test import TestCase

from conventions.models import Convention, Pret, Preteur
from core.tests import utils_assertions


class PretModelsTest(TestCase):
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

    @classmethod
    def setUpTestData(cls):
        convention = Convention.objects.get(numero="0001")
        Pret.objects.create(
            convention=convention,
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
        self.assertEqual(pret.p_full(), "Autre/Subventions")
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

    def test_xlsx(self):
        utils_assertions.assert_xlsx(self, Pret, "financement")

    def test_clone(self):
        pret = Pret.objects.first()
        pret.autre = "quelque chose"
        pret.numero = "001"
        pret.save()

        convention = Convention.objects.first()

        clone = pret.clone(convention=convention, autre="autre chose")

        self.assertEqual(clone.convention, convention)
        self.assertEqual(clone.numero, "001")
        self.assertEqual(clone.autre, "autre chose")
        for k in ("uuid", "id", "cree_le", "mis_a_jour_le"):
            self.assertNotEqual(getattr(clone, k), getattr(pret, k))
