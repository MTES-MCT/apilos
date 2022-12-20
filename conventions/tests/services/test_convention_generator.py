from datetime import date
import random
import unittest

from django.test import TestCase
from django.conf import settings
from bailleurs.models import SousNatureBailleur
from conventions.models import Convention, ConventionType1and2
from conventions.services.convention_generator import (
    ConventionTypeConfigurationError,
    default_str_if_none,
    get_convention_template_path,
    pluralize,
    to_fr_date,
    to_fr_date_or_default,
    to_fr_short_date,
    to_fr_short_date_or_default,
    typologie_label,
)
from core.tests import utils_fixtures
from programmes.models import NatureLogement, TypologieLogement
from users.models import User


class ConventionUtilGeneratorTest(unittest.TestCase):
    def test_pluralize(self):
        self.assertEqual(pluralize(0), "")
        self.assertEqual(pluralize(1), "")
        self.assertEqual(pluralize(2), "s")
        self.assertEqual(pluralize(random.randint(3, 999)), "s")


class ConventionServiceGeneratorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        pass

    def test_get_convention_template_path(self):
        user = User.objects.get(username="fix")
        convention = Convention.objects.get(numero="0001")
        avenant = convention.clone(user, convention_origin=convention)
        self.assertEqual(
            get_convention_template_path(avenant),
            f"{settings.BASE_DIR}/documents/Avenant-template.docx",
        )
        convention.programme.nature_logement = NatureLogement.AUTRE
        self.assertEqual(
            get_convention_template_path(convention),
            f"{settings.BASE_DIR}/documents/Foyer-template.docx",
        )
        for nature_logement in [
            NatureLogement.HEBERGEMENT,
            NatureLogement.RESISDENCESOCIALE,
            NatureLogement.PENSIONSDEFAMILLE,
            NatureLogement.RESIDENCEDACCUEIL,
            NatureLogement.RESIDENCEUNIVERSITAIRE,
            NatureLogement.RHVS,
        ]:
            convention.programme.nature_logement = nature_logement
            self.assertEqual(
                get_convention_template_path(convention),
                f"{settings.BASE_DIR}/documents/Residence-template.docx",
            )

        convention.programme.nature_logement = NatureLogement.LOGEMENTSORDINAIRES
        convention.programme.bailleur.sous_nature_bailleur = SousNatureBailleur.SEM_EPL
        self.assertEqual(
            get_convention_template_path(convention),
            f"{settings.BASE_DIR}/documents/SEM-template.docx",
        )

        for sous_nature in [
            SousNatureBailleur.OFFICE_PUBLIC_HLM,
            SousNatureBailleur.SA_HLM_ESH,
            SousNatureBailleur.COOPERATIVE_HLM_SCIC,
        ]:
            convention.programme.bailleur.sous_nature_bailleur = sous_nature
            self.assertEqual(
                get_convention_template_path(convention),
                f"{settings.BASE_DIR}/documents/HLM-template.docx",
            )

        for sous_nature in [
            SousNatureBailleur.ASSOCIATIONS,
        ]:
            convention.programme.bailleur.sous_nature_bailleur = sous_nature
            convention.type1and2 = ConventionType1and2.TYPE1
            self.assertEqual(
                get_convention_template_path(convention),
                f"{settings.BASE_DIR}/documents/Type1-template.docx",
            )
            convention.type1and2 = ConventionType1and2.TYPE2
            self.assertEqual(
                get_convention_template_path(convention),
                f"{settings.BASE_DIR}/documents/Type2-template.docx",
            )
            convention.type1and2 = None
            self.assertRaises(
                ConventionTypeConfigurationError,
                get_convention_template_path,
                convention,
            )

    def test_typologie_label(self):
        self.assertEqual(typologie_label(TypologieLogement.T1.label), "Logement T 1")
        self.assertEqual(
            typologie_label(TypologieLogement.T1prime.label), "Logement T 1'"
        )
        self.assertEqual(typologie_label(TypologieLogement.T7.label), "Logement T 7")
        self.assertEqual(typologie_label("Invalid value"), None)

    def test_default_str_if_none(self):
        self.assertEqual(default_str_if_none(None), "---")
        self.assertEqual(default_str_if_none(""), "---")
        self.assertEqual(default_str_if_none("None"), "None")

    def test_to_fr_date(self):
        self.assertEqual(to_fr_date(None), "")
        self.assertEqual(to_fr_date(""), "")
        self.assertEqual(to_fr_date(date(2022, 12, 31)), "31 décembre 2022")

    def test_to_fr_date_or_default(self):
        self.assertEqual(to_fr_date_or_default(None), "---")
        self.assertEqual(to_fr_date_or_default(""), "---")
        self.assertEqual(to_fr_date_or_default(date(2022, 12, 31)), "31 décembre 2022")

    def test_to_fr_short_date(self):
        self.assertEqual(to_fr_short_date(None), "")
        self.assertEqual(to_fr_short_date(""), "")
        self.assertEqual(to_fr_short_date(date(2022, 12, 31)), "31/12/2022")

    def test_to_fr_short_date_or_default(self):
        self.assertEqual(to_fr_short_date_or_default(None), "---")
        self.assertEqual(to_fr_short_date_or_default(""), "---")
        self.assertEqual(to_fr_short_date_or_default(date(2022, 12, 31)), "31/12/2022")
