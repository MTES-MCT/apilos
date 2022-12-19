import random
from datetime import date

from django.test import TestCase
from core.tests import utils_assertions, utils_fixtures

from programmes.models import (
    LocauxCollectifs,
    Programme,
    Lot,
    LogementEDD,
    Logement,
    Financement,
    ReferenceCadastrale,
    TypologieLogement,
    TypologieAnnexe,
    TypologieStationnement,
    TypeStationnement,
    TypeHabitat,
    TypeOperation,
    Annexe,
)


def params_logement(index):
    # pylint: disable=R0911
    if index <= 7:
        return TypologieLogement.T1, 0.9, 30, 0, 0, 30
    if index <= 10:
        return TypologieLogement.T1, 0.9, 30, 0, 0, 30
    if index <= 20:
        return TypologieLogement.T2, 1.0, 40, 5, 2.5, 42.5
    if index <= 30:
        return TypologieLogement.T3, 1.1, 55, 10, 5, 60
    if index <= 40:
        return TypologieLogement.T4, 1.1, 80, 20, 10, 90
    if index <= 45:
        return TypologieLogement.T5, 0.9, 100, 28, 12, 122
    return TypologieLogement.T6, 0.9, 110, 28, 12, 122


class ProgrammeModelsTest(TestCase):
    # pylint: disable=E1101 no-member
    @classmethod
    def setUpTestData(cls):
        bailleur = utils_fixtures.create_bailleur()
        programme = utils_fixtures.create_programme(bailleur)

        for financement in [Financement.PLAI, Financement.PLUS]:
            lot = Lot.objects.create(
                programme=programme,
                financement=financement,
                nb_logements=50,
            )
            for index in range(50):
                typologie, coef, sh, sa, sar, su = params_logement(index)
                LogementEDD.objects.create(
                    designation=("A" if financement == Financement.PLAI else "B")
                    + str(index),
                    programme=programme,
                    financement=financement,
                )
                logement = Logement.objects.create(
                    designation=("A" if financement == Financement.PLAI else "B")
                    + str(index),
                    lot=lot,
                    typologie=typologie,
                    surface_habitable=sh,
                    surface_annexes=sa,
                    surface_annexes_retenue=sar,
                    surface_utile=su,
                    loyer_par_metre_carre=5.1,
                    coeficient=coef,
                    loyer=su * coef * 5.1,
                )
                if sa > 0:
                    shsr = sar - sa
                    Annexe.objects.create(
                        logement=logement,
                        typologie=TypologieAnnexe.TERRASSE,
                        surface_hors_surface_retenue=shsr,
                        loyer_par_metre_carre=0.5,
                        loyer=shsr * 0.5,
                    )
            TypeStationnement.objects.create(
                lot=lot,
                typologie=TypologieStationnement.PLACE_STATIONNEMENT,
                nb_stationnements=random.randint(1, 10),
                loyer=random.randint(40, 75),
            )
            TypeStationnement.objects.create(
                lot=lot,
                typologie=TypologieStationnement.GARAGE_AERIEN,
                nb_stationnements=random.randint(1, 10),
                loyer=random.randint(40, 75),
            )

    def test_object_str(self):
        programme = Programme.objects.order_by("-uuid").first()
        expected_object_name = f"{programme.nom}"
        self.assertEqual(str(programme), expected_object_name)

        logement_edd = LogementEDD.objects.order_by("-uuid").first()
        expected_object_name = f"{logement_edd.designation}"
        self.assertEqual(str(logement_edd), expected_object_name)

        lot = Lot.objects.order_by("-uuid").first()
        expected_object_name = f"{lot.programme.nom} - {lot.financement}"
        self.assertEqual(str(lot), expected_object_name)

        logement = Logement.objects.order_by("-uuid").order_by("-uuid").first()
        expected_object_name = f"{logement.designation}"
        self.assertEqual(str(logement), expected_object_name)

        annexe = Annexe.objects.order_by("-uuid").first()
        expected_object_name = f"{annexe.typologie} - {annexe.logement.designation}"
        self.assertEqual(str(annexe), expected_object_name)

        stationnement = TypeStationnement.objects.order_by("-uuid").first()
        expected_object_name = (
            f"{stationnement.typologie} - "
            + f"{stationnement.lot.programme.nom} - {stationnement.lot.financement}"
        )
        self.assertEqual(str(stationnement), expected_object_name)

    def test_properties(self):
        logement = Logement.objects.order_by("uuid").first()
        self.assertEqual(logement.designation, logement.d)
        self.assertEqual(logement.get_typologie_display(), logement.t)
        self.assertEqual(logement.surface_habitable, logement.sh)
        self.assertEqual(logement.surface_annexes, logement.sa)
        self.assertEqual(logement.surface_annexes_retenue, logement.sar)
        self.assertEqual(logement.surface_utile, logement.su)
        self.assertEqual(logement.loyer_par_metre_carre, logement.lpmc)
        self.assertEqual(logement.coeficient, logement.c)
        self.assertEqual(logement.loyer, logement.l)

        annexe = Annexe.objects.order_by("uuid").first()
        self.assertEqual(annexe.get_typologie_display(), annexe.t)
        self.assertEqual(annexe.logement, annexe.lgt)
        self.assertEqual(annexe.surface_hors_surface_retenue, annexe.shsr)
        self.assertEqual(annexe.loyer_par_metre_carre, annexe.lpmc)
        self.assertEqual(annexe.loyer, annexe.l)

        stationnement = TypeStationnement.objects.order_by("uuid").first()
        self.assertEqual(stationnement.loyer, stationnement.l)
        self.assertEqual(stationnement.get_typologie_display(), stationnement.t)
        self.assertEqual(stationnement.nb_stationnements, stationnement.nb)

    def test_advanced_display(self):
        lot = Lot.objects.order_by("-uuid").first()
        type_habitat = random.choice(
            [TypeHabitat.INDIVIDUEL, TypeHabitat.COLLECTIF, TypeHabitat.MIXTE]
        )
        lot.type_habitat = type_habitat
        self.assertEqual(
            lot.get_type_habitat_advanced_display(0),
            " " + type_habitat.label.lower(),
        )
        self.assertEqual(
            lot.get_type_habitat_advanced_display(1),
            " " + type_habitat.label.lower(),
        )
        self.assertEqual(
            lot.get_type_habitat_advanced_display(2),
            " " + type_habitat.label.lower() + "s",
        )

        programme = Programme.objects.order_by("-uuid").first()
        programme.type_operation = TypeOperation.SANSOBJET
        self.assertEqual(programme.get_type_operation_advanced_display(), "")
        type_operation = random.choice(
            [
                TypeOperation.NEUF,
                TypeOperation.ACQUIS,
                TypeOperation.ACQUISAMELIORATION,
                TypeOperation.REHABILITATION,
                TypeOperation.USUFRUIT,
                TypeOperation.VEFA,
            ]
        )
        programme.type_operation = type_operation
        self.assertEqual(
            programme.get_type_operation_advanced_display(),
            " en " + type_operation.label.lower(),
        )
        programme.type_operation = TypeOperation.SANSTRAVAUX
        self.assertEqual(
            programme.get_type_operation_advanced_display(),
            " " + TypeOperation.SANSTRAVAUX.label.lower(),
        )

    def test_xlsx(self):
        utils_assertions.assert_xlsx(self, Annexe, "annexes")
        utils_assertions.assert_xlsx(self, ReferenceCadastrale, "cadastre")
        utils_assertions.assert_xlsx(self, LogementEDD, "logements_edd")
        utils_assertions.assert_xlsx(self, Logement, "logements")
        utils_assertions.assert_xlsx(self, LocauxCollectifs, "locaux_collectifs")
        utils_assertions.assert_xlsx(
            self,
            Logement,
            "foyer_residence_logements",
            import_mapping="foyer_residence_import_mapping",
        )
        utils_assertions.assert_xlsx(self, TypeStationnement, "stationnements")

    def test_get_text_and_files(self):
        programme = Programme.objects.order_by("-uuid").first()
        utils_assertions.assert_get_text_and_files(self, programme, "vendeur")
        utils_assertions.assert_get_text_and_files(self, programme, "acquereur")
        utils_assertions.assert_get_text_and_files(self, programme, "reference_notaire")
        utils_assertions.assert_get_text_and_files(
            self, programme, "reference_publication_acte"
        )
        utils_assertions.assert_get_files(self, programme, "acte_de_propriete")
        utils_assertions.assert_get_files(self, programme, "certificat_adressage")
        utils_assertions.assert_get_files(self, programme, "effet_relatif")
        utils_assertions.assert_get_files(self, programme, "reference_cadastrale")

        lot = Lot.objects.order_by("-uuid").first()
        utils_assertions.assert_get_text_and_files(self, lot, "edd_volumetrique")
        utils_assertions.assert_get_text_and_files(self, lot, "edd_classique")

    def test_date_achevement_compile(self):
        programme = Programme.objects.order_by("-uuid").first()
        programme.date_achevement = None
        programme.date_achevement_previsible = None
        programme.save()
        self.assertIsNone(programme.date_achevement_compile)
        programme.date_achevement = date(2022, 6, 1)
        programme.date_achevement_previsible = date(2022, 12, 31)
        programme.save()
        self.assertEqual(programme.date_achevement_compile, date(2022, 6, 1))
        programme.date_achevement = date(2022, 6, 1)
        programme.date_achevement_previsible = None
        programme.save()
        self.assertEqual(programme.date_achevement_compile, date(2022, 6, 1))
        programme.date_achevement = None
        programme.date_achevement_previsible = date(2022, 12, 31)
        programme.save()
        self.assertEqual(programme.date_achevement_compile, date(2022, 12, 31))


class LotModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def test_mixity_option(self):
        lot = Lot.objects.order_by("uuid").first()
        lot.financement = Financement.PLUS
        lot.lgts_mixite_sociale_negocies = random.randint(1, 10)
        self.assertTrue(lot.mixity_option())
        self.assertEqual(
            lot.lgts_mixite_sociale_negocies, lot.lgts_mixite_sociale_negocies_display()
        )
        for k, _ in Financement.choices:
            if k != Financement.PLUS:
                lot.financement = k
                self.assertFalse(lot.mixity_option())
                self.assertEqual(0, lot.lgts_mixite_sociale_negocies_display())

    def test_lot_bailleur(self):
        lot = Lot.objects.order_by("uuid").first()
        self.assertEqual(lot.bailleur, lot.programme.bailleur)
