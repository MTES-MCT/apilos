from datetime import date
from django.test import TestCase

from programmes.models import IndiceEvolutionLoyer, NatureLogement
from programmes.services import LoyerRedevanceUpdateComputer


class LoyerRedevanceUpdateComputerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = {
            NatureLogement.LOGEMENTSORDINAIRES: {
                2019: 25,
                2020: 0,
                2022: 20,
            },
            NatureLogement.RESISDENCESOCIALE: {
                2019: 20,
                2020: 0,
                2022: 10,
            },
        }

        for nature_logement, indices in data.items():
            for annee, differentiel in indices.items():
                IndiceEvolutionLoyer.objects.update_or_create(
                    annee=annee,
                    nature_logement=nature_logement,
                    defaults=dict(
                        annee=annee,
                        nature_logement=nature_logement,
                        differentiel=differentiel,
                    ),
                )

    def test_compute_loyer_update_logements_ordinaires(self):
        """
        Teste que pour un logement ordinaire, le loyer est éligible à révisions sur différentes périodes
        """
        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            date_initiale=date.fromisoformat("2018-10-20"),
            date_actualisation=date.fromisoformat("2020-03-18"),
        )
        self.assertEqual(500, update)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            date_initiale=date.fromisoformat("2018-10-20"),
        )
        self.assertEqual(600, update)

    def test_compute_loyer_update_residences_sociales(self):
        """
        Teste que pour une résidence sociale, la redevance est éligible à révisions sur différentes périodes
        """

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=250,
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            date_initiale=date.fromisoformat("2018-10-20"),
            date_actualisation=date.fromisoformat("2020-03-18"),
        )
        self.assertEqual(300, update)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=250,
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            date_initiale=date.fromisoformat("2018-10-20"),
        )
        self.assertEqual(330, update)

    def test_compute_loyer_update_residences_d_accueil(self):
        """
        Teste que pour un logement dont la nature n'a aucun indice connu sur la période, le loyer demeure inchangeable
        """
        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=117,
            nature_logement=NatureLogement.RESIDENCEDACCUEIL,
            date_initiale=date.fromisoformat("2018-10-20"),
            date_actualisation=date.fromisoformat("2020-03-18"),
        )
        self.assertEqual(117, update)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=117,
            nature_logement=NatureLogement.RESIDENCEDACCUEIL,
            date_initiale=date.fromisoformat("2018-10-20"),
        )
        self.assertEqual(117, update)
