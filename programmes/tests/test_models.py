import random
from datetime import date

from django.forms import model_to_dict
from django.test import TestCase

from bailleurs.models import Bailleur
from core.tests import utils_assertions, utils_fixtures
from instructeurs.models import Administration
from programmes.models import (
    Annexe,
    Financement,
    LocauxCollectifs,
    Logement,
    LogementEDD,
    Lot,
    NatureLogement,
    Programme,
    ReferenceCadastrale,
    TypeHabitat,
    TypeOperation,
    TypeStationnement,
    TypologieAnnexe,
    TypologieLogement,
    TypologieStationnement,
)


def params_logement(index):
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
    fixtures = ["departements.json"]

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
        utils_assertions.assert_get_text_and_files(
            self, programme, "edd_stationnements"
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

    def test_is_residence(self):
        programme = Programme.objects.order_by("-uuid").first()
        for nature_logement in [
            NatureLogement.HEBERGEMENT,
            NatureLogement.PENSIONSDEFAMILLE,
            NatureLogement.RESIDENCEDACCUEIL,
            NatureLogement.RESISDENCESOCIALE,
        ]:
            programme.nature_logement = nature_logement
            self.assertTrue(programme.is_residence())
        for nature_logement in [
            NatureLogement.LOGEMENTSORDINAIRES,
            NatureLogement.AUTRE,
            NatureLogement.RESIDENCEUNIVERSITAIRE,
            NatureLogement.RHVS,
        ]:
            programme.nature_logement = nature_logement
            self.assertFalse(programme.is_residence())

    def test_code_insee(self):
        bailleur = Bailleur.objects.all().order_by("uuid").first()
        administration = Administration.objects.all().order_by("uuid").first()
        programme_75 = Programme.objects.create(
            nom="test",
            code_postal="75001",
            bailleur=bailleur,
            administration=administration,
        )
        self.assertEqual(programme_75.code_insee_departement, "75")
        self.assertEqual(programme_75.code_insee_region, "11")

        programme_00 = Programme.objects.create(
            nom="test",
            code_postal="00001",
            bailleur=bailleur,
            administration=administration,
        )
        self.assertIsNone(programme_00.code_insee_departement)
        self.assertIsNone(programme_00.code_insee_region)

        programme_20 = Programme.objects.create(
            nom="test",
            code_postal="20001",
            bailleur=bailleur,
            administration=administration,
        )
        self.assertEqual(programme_20.code_insee_departement, "20")
        self.assertEqual(programme_20.code_insee_region, "94")

    def test_clone(self):
        programme = Programme.objects.order_by("-uuid").first()
        self.assertIsNone(programme.parent_id)
        cloned_programme1 = programme.clone()
        self.assertEqual(cloned_programme1.parent_id, programme.id)
        self.assertEqual(cloned_programme1.bailleur_id, programme.bailleur_id)
        self.assertEqual(
            cloned_programme1.administration_id, programme.administration_id
        )
        cloned_programme2 = cloned_programme1.clone()
        self.assertEqual(cloned_programme2.parent_id, programme.id)
        self.assertEqual(cloned_programme2.bailleur_id, programme.bailleur_id)
        self.assertEqual(
            cloned_programme2.administration_id, programme.administration_id
        )

    def test_edd_stationnements_text(self):
        programme = programme = Programme.objects.order_by("-uuid").first()
        self.assertEqual(programme.edd_stationnements_text(), "EDD stationnements")

    def test_edd_stationnements_files(self):
        programme = programme = Programme.objects.order_by("-uuid").first()
        self.assertDictEqual(
            programme.edd_stationnements_files(),
            {
                "fbb9890f-171b-402d-a35e-71e1bd791b70": {
                    "uuid": "fbb9890f-171b-402d-a35e-71e1bd791b70",
                    "thumbnail": "data:image/png;base64,BLAHBLAH==",
                    "size": "31185",
                    "filename": "acquereur1.png",
                    "content_type": "image/png",
                },
                "dccd310d-2e50-45d8-a477-db7b08ae1d71": {
                    "uuid": "dccd310d-2e50-45d8-a477-db7b08ae1d71",
                    "thumbnail": "data:image/png;base64,BLIHBLIH==",
                    "size": "69076",
                    "filename": "acquereur2.png",
                    "content_type": "image/png",
                },
            },
        )


class LotModelsTest(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def test_mixity_option(self):
        lot = Lot.objects.order_by("uuid").first()
        for financement in [Financement.PLUS, Financement.PLUS_CD]:
            lot.financement = financement
            lot.lgts_mixite_sociale_negocies = random.randint(1, 10)
            self.assertTrue(lot.mixity_option())
            self.assertEqual(
                lot.lgts_mixite_sociale_negocies,
                lot.lgts_mixite_sociale_negocies_display(),
            )
        for financement in [
            k
            for (k, _) in Financement.choices
            if k not in [Financement.PLUS, Financement.PLUS_CD]
        ]:
            lot.financement = financement
            self.assertFalse(lot.mixity_option())
            self.assertEqual(0, lot.lgts_mixite_sociale_negocies_display())

    def test_lot_bailleur(self):
        lot = Lot.objects.order_by("uuid").first()
        self.assertEqual(lot.bailleur, lot.programme.bailleur)

    def test_clone(self):
        lot = Lot.objects.order_by("-uuid").first()
        cloned_programme1 = lot.programme.clone()
        cloned_lot1 = lot.clone(cloned_programme1)

        self.assertIsNone(lot.parent_id)
        self.assertEqual(cloned_lot1.parent_id, lot.id)
        self.assertEqual(cloned_lot1.programme_id, cloned_programme1.id)

        cloned_programme2 = cloned_programme1.clone()
        cloned_lot2 = cloned_lot1.clone(cloned_programme2)

        self.assertEqual(cloned_lot2.parent_id, lot.id)
        self.assertEqual(cloned_lot2.programme_id, cloned_programme2.id)


class ReferenceCadastraleTest(TestCase):
    def test_compute_surface(self):
        self.assertEqual(
            ReferenceCadastrale.compute_surface(529814), "52 ha 98 a 14 ca"
        )
        self.assertEqual(ReferenceCadastrale.compute_surface(), "0 ha 0 a 0 ca")


class LogementModelsTest(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self):
        super().setUp()
        self.lot = Lot.objects.order_by("-uuid").first()
        for designation in ["B1", "B2"]:
            Logement.objects.create(
                designation=designation,
                lot=self.lot,
                typologie=TypologieLogement.T1,
                surface_habitable=10.00,
                surface_annexes=10.00,
                surface_annexes_retenue=5.00,
                surface_utile=15.00,
                loyer_par_metre_carre=5,
                coeficient=1.0000,
                loyer=75.00,
            )

    def test_clone(self):
        cloned_programme1 = self.lot.programme.clone()
        cloned_lot1 = self.lot.clone(cloned_programme1)

        logement = self.lot.logements.get(designation="B1")
        self.assertEqual(logement.typologie, TypologieLogement.T1)

        Annexe.objects.create(
            logement=logement,
            typologie=logement.typologie,
            surface_hors_surface_retenue=5,
            loyer_par_metre_carre=0.1,
            loyer=0.5,
        )
        cloned_logement = logement.clone(cloned_lot1, typologie=TypologieLogement.T1BIS)

        annexe = logement.annexes.get(logement__designation="B1")
        cloned_annexe = cloned_logement.annexes.get(logement__designation="B1")

        fields = [
            "designation",
            "surface_habitable",
            "surface_annexes",
            "surface_annexes_retenue",
            "surface_utile",
            "loyer_par_metre_carre",
            "coeficient",
            "loyer",
        ]
        self.assertEqual(
            model_to_dict(logement, fields=fields),
            model_to_dict(cloned_logement, fields=fields),
        )
        self.assertEqual(cloned_logement.typologie, TypologieLogement.T1BIS)

        annexe_fields = [
            "typologie",
            "surface_hors_surface_retenue",
            "loyer_par_metre_carre",
            "loyer",
        ]
        self.assertEqual(
            model_to_dict(annexe, fields=annexe_fields),
            model_to_dict(cloned_annexe, fields=annexe_fields),
        )
