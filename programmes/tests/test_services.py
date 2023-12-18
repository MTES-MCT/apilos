from datetime import date

from django.test import TestCase

from programmes.models import IndiceEvolutionLoyer, NatureLogement
from programmes.services import LoyerRedevanceUpdateComputer


class LoyerRedevanceUpdateComputerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = [
            {
                "annee": 2023,
                "evolution": 3.6,
                "date_debut": "2022-01-01",
                "date_fin": "2022-12-31",
            },
            {
                "annee": 2022,
                "evolution": 0.42,
                "date_debut": "2021-01-01",
                "date_fin": "2021-12-31",
            },
            {
                "annee": 2021,
                "evolution": 0.66,
                "date_debut": "2020-01-01",
                "date_fin": "2020-12-31",
            },
            {
                "annee": 2020,
                "evolution": 1.53,
                "date_debut": "2019-01-01",
                "date_fin": "2019-12-31",
            },
            {
                "annee": 2019,
                "evolution": 1.25,
                "date_debut": "2018-01-01",
                "date_fin": "2018-12-31",
            },
            {
                "annee": 2018,
                "evolution": 0,
                "date_debut": "2017-01-01",
                "date_fin": "2017-12-31",
            },
            {
                "annee": 2017,
                "evolution": 0,
                "date_debut": "2016-01-01",
                "date_fin": "2016-12-31",
            },
            {
                "annee": 2016,
                "evolution": 0.08,
                "date_debut": "2015-01-01",
                "date_fin": "2015-12-31",
            },
            {
                "annee": 2015,
                "evolution": 0.57,
                "date_debut": "2014-01-01",
                "date_fin": "2014-12-31",
            },
            {
                "annee": 2014,
                "evolution": 1.2,
                "date_debut": "2013-01-01",
                "date_fin": "2013-12-31",
            },
            {
                "annee": 2013,
                "evolution": 2.2,
                "date_debut": "2012-01-01",
                "date_fin": "2012-12-31",
            },
            {
                "annee": 2012,
                "evolution": 1.73,
                "date_debut": "2011-01-01",
                "date_fin": "2011-12-31",
            },
            {
                "annee": 2011,
                "evolution": 0.57,
                "date_debut": "2010-01-01",
                "date_fin": "2010-12-31",
            },
            {
                "annee": 2010,
                "evolution": 0.04,
                "date_debut": "2009-07-01",
                "date_fin": "2009-12-31",
            },
            {
                "annee": 2009,
                "evolution": 2.83,
                "date_debut": "2008-07-01",
                "date_fin": "2009-06-30",
            },
            {
                "annee": 2008,
                "evolution": 1.36,
                "date_debut": "2007-07-01",
                "date_fin": "2008-06-30",
            },
            {
                "annee": 2007,
                "evolution": 3.23,
                "date_debut": "2006-07-01",
                "date_fin": "2007-06-30",
            },
        ]

        for annee in data:
            for nature_logement in [
                NatureLogement.AUTRE,
                NatureLogement.RESISDENCESOCIALE,
                NatureLogement.RESIDENCEDACCUEIL,
                NatureLogement.LOGEMENTSORDINAIRES,
            ]:
                is_loyer = nature_logement == NatureLogement.LOGEMENTSORDINAIRES
                nature_logement = nature_logement if not is_loyer else None
                IndiceEvolutionLoyer.objects.update_or_create(
                    annee=annee["annee"],
                    is_loyer=is_loyer,
                    nature_logement=nature_logement,
                    defaults=dict(
                        annee=annee["annee"],
                        is_loyer=is_loyer,
                        nature_logement=nature_logement,
                        date_debut=annee["date_debut"],
                        date_fin=annee["date_fin"],
                        evolution=annee["evolution"],
                    ),
                )

    def test_compute_loyer_update_logements_ordinaires(self):
        """
        Teste que pour un logement ordinaire, le loyer est éligible à révisions
        sur différentes périodes
        """
        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=10,
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            date_initiale=date.fromisoformat("2008-04-06"),
            date_actualisation=date.fromisoformat("2023-04-06"),
        )
        self.assertAlmostEqual(11.96, update, places=2)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            date_initiale=date.fromisoformat("2013-07-12"),
            date_actualisation=date.fromisoformat("2014-03-18"),
        )
        self.assertAlmostEqual(400 * 1.012, update, places=2)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=100,
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            date_initiale=date.fromisoformat("2014-02-01"),
        )
        self.assertAlmostEqual(
            100 * 1.0057 * 1.0008 * 1.0125 * 1.0153 * 1.0066 * 1.0042 * 1.036,
            update,
            places=2,
        )

    def test_compute_loyer_update_residences_sociales(self):
        """
        Teste que pour une résidence sociale, la redevance est éligible à
        révisions sur différentes périodes
        """

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            date_initiale=date.fromisoformat("2013-07-12"),
            date_actualisation=date.fromisoformat("2014-03-18"),
        )
        self.assertAlmostEqual(400 * 1.012, update, places=2)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=100,
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            date_initiale=date.fromisoformat("2014-02-01"),
        )
        self.assertAlmostEqual(
            100 * 1.0057 * 1.0008 * 1.0125 * 1.0153 * 1.0066 * 1.0042 * 1.036,
            update,
            places=2,
        )

    def test_compute_loyer_update_residences_d_accueil(self):
        """
        Teste que pour une résidence sociale, la redevance est éligible
        à révisions sur différentes périodes
        """
        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.RESIDENCEDACCUEIL,
            date_initiale=date.fromisoformat("2013-07-12"),
            date_actualisation=date.fromisoformat("2014-03-18"),
        )
        self.assertAlmostEqual(400 * 1.012, update, places=2)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=100,
            nature_logement=NatureLogement.RESIDENCEDACCUEIL,
            date_initiale=date.fromisoformat("2014-02-01"),
        )
        self.assertAlmostEqual(
            100 * 1.0057 * 1.0008 * 1.0125 * 1.0153 * 1.0066 * 1.0042 * 1.036,
            update,
            places=2,
        )

    def test_compute_loyer_update_pensions_de_famille(self):
        """
        Teste que pour un logement de nature incompatible (pension de famille,
        résidence universitaire, hébergement) avec la calculette, une exception
        est levée
        """
        with self.assertRaises(Exception):
            LoyerRedevanceUpdateComputer.compute_loyer_update(
                montant_initial=400,
                nature_logement=NatureLogement.PENSIONSDEFAMILLE,
                date_initiale=date.fromisoformat("2013-07-12"),
            )

        with self.assertRaises(Exception):
            LoyerRedevanceUpdateComputer.compute_loyer_update(
                montant_initial=400,
                nature_logement=NatureLogement.HEBERGEMENT,
                date_initiale=date.fromisoformat("2013-07-12"),
            )

        with self.assertRaises(Exception):
            LoyerRedevanceUpdateComputer.compute_loyer_update(
                montant_initial=400,
                nature_logement=NatureLogement.RESIDENCEUNIVERSITAIRE,
                date_initiale=date.fromisoformat("2013-07-12"),
            )
