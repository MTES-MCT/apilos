from datetime import date
from django.test import TestCase

from programmes.models import IndiceEvolutionLoyer, NatureLogement
from programmes.services import LoyerRedevanceUpdateComputer


class LoyerRedevanceUpdateComputerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = {
            2014: 1.2,
            2015: 0.57,
            2016: 0.08,
            2017: 0,
            2018: 0,
            2019: 1.25,
            2020: 1.53,
            2021: 0.66,
            2022: 0.42,
        }

        for annee, evolution in data.items():
            for nature_logement in [
                NatureLogement.AUTRE,
                NatureLogement.RESISDENCESOCIALE,
                NatureLogement.RESIDENCEDACCUEIL,
                NatureLogement.LOGEMENTSORDINAIRES,
            ]:
                is_loyer = nature_logement != NatureLogement.LOGEMENTSORDINAIRES
                nature_logement = nature_logement if is_loyer else None
                IndiceEvolutionLoyer.objects.update_or_create(
                    annee=annee,
                    is_loyer=is_loyer,
                    nature_logement=nature_logement,
                    defaults=dict(
                        annee=annee,
                        is_loyer=is_loyer,
                        nature_logement=nature_logement,
                        evolution=evolution,
                    ),
                )

    def test_compute_loyer_update_logements_ordinaires(self):
        """
        Teste que pour un logement ordinaire, le loyer est éligible à révisions sur différentes périodes
        """
        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            date_initiale=date.fromisoformat("2013-07-12"),
            date_actualisation=date.fromisoformat("2014-03-18"),
        )
        self.assertEqual(400 * 1.012, update)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=100,
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            date_initiale=date.fromisoformat("2014-02-01"),
        )
        self.assertEqual(
            100 * 1.0057 * 1.0008 * 1.0125 * 1.0153 * 1.0066 * 1.0042, update
        )

    def test_compute_loyer_update_residences_sociales(self):
        """
        Teste que pour une résidence sociale, la redevance est éligible à révisions sur différentes périodes
        """

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            date_initiale=date.fromisoformat("2013-07-12"),
            date_actualisation=date.fromisoformat("2014-03-18"),
        )
        self.assertEqual(400 * 1.012, update)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=100,
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            date_initiale=date.fromisoformat("2014-02-01"),
        )
        self.assertEqual(
            100 * 1.0057 * 1.0008 * 1.0125 * 1.0153 * 1.0066 * 1.0042, update
        )

    def test_compute_loyer_update_residences_d_accueil(self):
        """
        Teste que pour une résidence sociale, la redevance est éligible à révisions sur différentes périodes
        """
        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.RESIDENCEDACCUEIL,
            date_initiale=date.fromisoformat("2013-07-12"),
            date_actualisation=date.fromisoformat("2014-03-18"),
        )
        self.assertEqual(400 * 1.012, update)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=100,
            nature_logement=NatureLogement.RESIDENCEDACCUEIL,
            date_initiale=date.fromisoformat("2014-02-01"),
        )
        self.assertEqual(
            100 * 1.0057 * 1.0008 * 1.0125 * 1.0153 * 1.0066 * 1.0042, update
        )

    def test_compute_loyer_update_pensions_de_famille(self):
        with self.assertRaises(Exception):
            LoyerRedevanceUpdateComputer.compute_loyer_update(
                montant_initial=400,
                nature_logement=NatureLogement.PENSIONSDEFAMILLE,
                date_initiale=date.fromisoformat("2013-07-12"),
            )
