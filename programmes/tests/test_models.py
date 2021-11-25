import random
from datetime import date

from django.test import TestCase
from core.tests import utils

from programmes.models import (
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
    if index <= 10:
        return TypologieLogement.T1, 0.9, 30, 0, 0, 30
    if index <= 20:
        return TypologieLogement.T2, 1.0, 40, 5, 2.5, 42.5
    if index <= 30:
        return TypologieLogement.T3, 1.1, 55, 10, 5, 60
    if index <= 40:
        return TypologieLogement.T4, 1.1, 80, 20, 10, 90
    return TypologieLogement.T5, 0.9, 110, 28, 12, 122


class ProgrammeModelsTest(TestCase):
    # pylint: disable=E1101 no-member
    @classmethod
    def setUpTestData(cls):
        bailleur = utils.create_bailleur()
        programme = utils.create_programme(bailleur)

        count = 0
        for financement in [Financement.PLAI, Financement.PLUS]:
            count += 1
            lot = Lot.objects.create(
                numero=count,
                bailleur=bailleur,
                programme=programme,
                financement=financement,
                nb_logements=50,
            )
            for index in range(50):
                typologie, coef, sh, sa, sar, su = params_logement(index)
                LogementEDD.objects.create(
                    designation=("A" if financement == Financement.PLAI else "B")
                    + str(index),
                    bailleur=bailleur,
                    programme=programme,
                    financement=financement,
                    typologie=typologie,
                )
                logement = Logement.objects.create(
                    designation=("A" if financement == Financement.PLAI else "B")
                    + str(index),
                    bailleur=bailleur,
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
                        bailleur=bailleur,
                        logement=logement,
                        typologie=TypologieAnnexe.TERRASSE,
                        surface_hors_surface_retenue=shsr,
                        loyer_par_metre_carre=0.5,
                        loyer=shsr * 0.5,
                    )
            TypeStationnement.objects.create(
                bailleur=bailleur,
                lot=lot,
                typologie=TypologieStationnement.PLACE_STATIONNEMENT,
                nb_stationnements=random.randint(1, 10),
                loyer=random.randint(40, 75),
            )
            TypeStationnement.objects.create(
                bailleur=bailleur,
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
        programme = Programme.objects.order_by("-uuid").first()
        programme.type_habitat = TypeHabitat.SANSOBJET
        self.assertEqual(programme.get_type_habitat_advanced_display(), "")
        self.assertEqual(programme.get_type_habitat_advanced_display(1), "")
        self.assertEqual(programme.get_type_habitat_advanced_display(2), "")
        type_habitat = random.choice([TypeHabitat.INDIVIDUEL, TypeHabitat.COLLECTIF])
        programme.type_habitat = type_habitat
        self.assertEqual(
            programme.get_type_habitat_advanced_display(0),
            " " + type_habitat.label.lower(),
        )
        self.assertEqual(
            programme.get_type_habitat_advanced_display(1),
            " " + type_habitat.label.lower(),
        )
        self.assertEqual(
            programme.get_type_habitat_advanced_display(2),
            " " + type_habitat.label.lower() + "s",
        )

        programme.type_operation = TypeOperation.SANSOBJET
        self.assertEqual(programme.get_type_operation_advanced_display(), "")
        type_operation = random.choice(
            [
                TypeOperation.NEUF,
                TypeOperation.ACQUIS,
                TypeOperation.DEMEMBREMENT,
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
        utils.assert_xlsx(self, Annexe, "annexes")
        utils.assert_xlsx(self, ReferenceCadastrale, "cadastre")
        utils.assert_xlsx(self, LogementEDD, "logements_edd")
        utils.assert_xlsx(self, Logement, "logements")
        utils.assert_xlsx(self, TypeStationnement, "stationnements")

    def test_get_text_and_files(self):
        programme = Programme.objects.order_by("-uuid").first()
        utils.assert_get_text_and_files(self, programme, "vendeur")
        utils.assert_get_text_and_files(self, programme, "acquereur")
        utils.assert_get_text_and_files(self, programme, "reference_notaire")
        utils.assert_get_text_and_files(self, programme, "reference_publication_acte")
        utils.assert_get_text_and_files(self, programme, "edd_volumetrique")
        utils.assert_get_text_and_files(self, programme, "edd_classique")
        utils.assert_get_files(self, programme, "acte_de_propriete")
        utils.assert_get_files(self, programme, "acte_notarial")
        utils.assert_get_files(self, programme, "reference_cadastrale")

    def test_date_commisioning(self):
        programme = Programme.objects.order_by("-uuid").first()
        programme.date_achevement = None
        programme.date_achevement_previsible = None
        self.assertEqual(programme.date_commisioning(), "NC")
        programme.date_achevement = date(2022, 6, 1)
        programme.date_achevement_previsible = date(2022, 12, 31)
        self.assertEqual(programme.date_commisioning(), date(2022, 6, 1))
        programme.date_achevement = date(2022, 6, 1)
        programme.date_achevement_previsible = None
        self.assertEqual(programme.date_commisioning(), date(2022, 6, 1))
        programme.date_achevement = None
        programme.date_achevement_previsible = date(2022, 12, 31)
        self.assertEqual(programme.date_commisioning(), date(2022, 12, 31))
