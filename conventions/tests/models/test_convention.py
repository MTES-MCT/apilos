import datetime
import uuid
from unittest import mock

import pytest
from django.test import TestCase

from conventions.models import Convention, ConventionHistory, ConventionStatut
from conventions.tests.factories import ConventionFactory
from programmes.models import Financement
from users.models import User
from users.type_models import EmailPreferences, TypeRole


class ConventionModelsTest(TestCase):
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

    def test_object_str(self):
        convention = Convention.objects.get(numero="0001")
        lot = convention.lot
        type_habitat = lot.get_type_habitat_display()
        programme = convention.programme
        expected_object_name = (
            f"{programme.ville} - {programme.nom} - "
            + f"{lot.nb_logements} lgts - {type_habitat} - {lot.financement}"
        )
        self.assertEqual(str(convention), expected_object_name)

    def test_is_functions(self):
        convention = Convention.objects.get(numero="0001")
        self.assertTrue(convention.is_bailleur_editable())
        convention.statut = ConventionStatut.INSTRUCTION.label
        self.assertFalse(convention.is_bailleur_editable())
        convention.statut = ConventionStatut.CORRECTION.label
        self.assertTrue(convention.is_bailleur_editable())
        convention.statut = ConventionStatut.A_SIGNER.label
        self.assertFalse(convention.is_bailleur_editable())
        convention.statut = ConventionStatut.SIGNEE.label
        self.assertFalse(convention.is_bailleur_editable())
        convention.statut = ConventionStatut.RESILIEE.label
        self.assertFalse(convention.is_bailleur_editable())

    def test_get_email_bailleur_users(self):
        convention = Convention.objects.get(numero="0001")
        raph = User.objects.get(username="raph")
        self.assertEqual(convention.get_email_bailleur_users(), [raph.email])
        raph.preferences_email = EmailPreferences.AUCUN
        raph.save()
        self.assertEqual(convention.get_email_bailleur_users(), [])
        raph.preferences_email = EmailPreferences.PARTIEL
        raph.save()
        self.assertEqual(convention.get_email_bailleur_users(), [])
        ConventionHistory.objects.create(
            convention=convention,
            statut_convention=ConventionStatut.INSTRUCTION.label,
            statut_convention_precedent=ConventionStatut.PROJET.label,
            user=raph,
        ).save()
        self.assertEqual(convention.get_email_bailleur_users(), [raph.email])

    def test_get_email_inctructeur_users(self):
        convention = Convention.objects.get(numero="0001")
        fix = User.objects.get(username="fix")
        self.assertEqual(convention.get_email_instructeur_users(), [fix.email])
        fix.preferences_email = EmailPreferences.AUCUN
        fix.save()
        self.assertEqual(convention.get_email_instructeur_users(), [])
        fix.preferences_email = EmailPreferences.PARTIEL
        fix.save()
        self.assertEqual(convention.get_email_instructeur_users(), [])
        self.assertEqual(
            convention.get_email_instructeur_users(include_partial=True), [fix.email]
        )
        ConventionHistory.objects.create(
            convention=convention,
            statut_convention=ConventionStatut.INSTRUCTION.label,
            statut_convention_precedent=ConventionStatut.PROJET.label,
            user=fix,
        ).save()
        self.assertEqual(convention.get_email_instructeur_users(), [fix.email])

    def test_statut_for_template(self):
        convention = Convention.objects.order_by("uuid").first()
        convention.statut = ConventionStatut.PROJET.label
        self.assertEqual(convention.statut_for_template()["statut"], "1. Projet")
        self.assertEqual(
            convention.statut_for_template()["statut_display"],
            "1. Projet",
        )
        self.assertEqual(convention.statut_for_template()["key_statut"], "Projet")
        convention.statut = ConventionStatut.INSTRUCTION.label
        self.assertEqual(
            convention.statut_for_template()["statut"], "2. Instruction requise"
        )
        self.assertEqual(
            convention.statut_for_template()["statut_display"],
            "2. Instruction requise",
        )
        self.assertEqual(
            convention.statut_for_template()["key_statut"], "Instruction_requise"
        )
        convention.statut = ConventionStatut.CORRECTION.label
        self.assertEqual(
            convention.statut_for_template()["statut"], "3. Corrections requises"
        )
        self.assertEqual(
            convention.statut_for_template()["statut_display"],
            "3. Corrections requises",
        )
        self.assertEqual(
            convention.statut_for_template()["key_statut"], "Corrections_requises"
        )
        convention.statut = ConventionStatut.A_SIGNER.label
        self.assertEqual(convention.statut_for_template()["statut"], "4. A signer")
        self.assertEqual(
            convention.statut_for_template()["statut_display"], "4. A signer"
        )
        self.assertEqual(convention.statut_for_template()["key_statut"], "A_signer")
        convention.statut = ConventionStatut.SIGNEE.label
        self.assertEqual(convention.statut_for_template()["statut"], "5. Signée")
        self.assertEqual(
            convention.statut_for_template()["statut_display"], "5. Signée"
        )
        self.assertEqual(convention.statut_for_template()["key_statut"], "Signee")

    def test_short_statut_for_bailleur(self):
        convention = Convention.objects.order_by("uuid").first()
        convention.statut = ConventionStatut.PROJET.label
        self.assertEqual(convention.short_statut_for_bailleur(), "En projet")
        convention.statut = ConventionStatut.INSTRUCTION.label
        self.assertEqual(convention.short_statut_for_bailleur(), "En instruction")
        convention.statut = ConventionStatut.CORRECTION.label
        self.assertEqual(convention.short_statut_for_bailleur(), "À corriger")
        convention.statut = ConventionStatut.A_SIGNER.label
        self.assertEqual(convention.short_statut_for_bailleur(), "À signer")
        convention.statut = ConventionStatut.SIGNEE.label
        self.assertEqual(convention.short_statut_for_bailleur(), "Finalisée")
        convention.statut = ConventionStatut.RESILIEE.label
        self.assertEqual(convention.short_statut_for_bailleur(), "Résiliée")

    def test_short_statut_for_instructeur(self):
        convention = Convention.objects.order_by("uuid").first()
        convention.statut = ConventionStatut.PROJET.label
        self.assertEqual(convention.short_statut_for_instructeur(), "En projet")
        convention.statut = ConventionStatut.INSTRUCTION.label
        self.assertEqual(convention.short_statut_for_instructeur(), "À instruire")
        convention.statut = ConventionStatut.CORRECTION.label
        self.assertEqual(convention.short_statut_for_instructeur(), "En correction")
        convention.statut = ConventionStatut.A_SIGNER.label
        self.assertEqual(convention.short_statut_for_instructeur(), "À signer")
        convention.statut = ConventionStatut.SIGNEE.label
        self.assertEqual(convention.short_statut_for_instructeur(), "Finalisée")
        convention.statut = ConventionStatut.RESILIEE.label
        self.assertEqual(convention.short_statut_for_instructeur(), "Résiliée")

    def test_mixity_option(self):
        convention = Convention.objects.order_by("uuid").first()
        for financement in [Financement.PLUS, Financement.PLUS_CD]:
            convention.financement = financement
            self.assertTrue(convention.mixity_option())
        for financement in [
            k
            for (k, _) in Financement.choices
            if k not in [Financement.PLUS, Financement.PLUS_CD]
        ]:
            convention.financement = financement
            self.assertFalse(convention.mixity_option())

    def test_display_not_validated_status(self):
        convention = Convention.objects.order_by("uuid").first()
        convention.statut = ConventionStatut.PROJET.label
        self.assertEqual(
            convention.display_not_validated_status(), "Projet de convention"
        )
        convention.statut = ConventionStatut.INSTRUCTION.label
        self.assertEqual(
            convention.display_not_validated_status(),
            "Convention en cours d'instruction",
        )
        convention.statut = ConventionStatut.CORRECTION.label
        self.assertEqual(
            convention.display_not_validated_status(),
            "Convention en cours d'instruction",
        )
        convention.statut = ConventionStatut.A_SIGNER.label
        self.assertEqual(convention.display_not_validated_status(), "")
        convention.statut = ConventionStatut.SIGNEE.label
        self.assertEqual(convention.display_not_validated_status(), "")

    def test_convention_bailleur(self):
        convention = Convention.objects.order_by("uuid").first()
        self.assertEqual(convention.bailleur, convention.programme.bailleur)


class ConventionPrefixTest(TestCase):
    fixtures = [
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
    ]

    def clone_convention(self, convention):
        programme = convention.programme
        programme.pk = None
        programme.uuid = uuid.uuid4()
        programme.save()
        lot = convention.lot
        convention.pk = None
        convention.uuid = uuid.uuid4()
        convention.programme = programme
        convention.save()
        lot.pk = None
        lot.uuid = uuid.uuid4()
        lot.convention = convention
        lot.save()
        return convention

    def test_get_convention_prefix_same_admin(self):
        current_year = datetime.date.today().year % 100
        convention = Convention.objects.order_by("uuid").first()
        self.assertEqual(
            convention.get_convention_prefix(), f"13.67890.{current_year}.0001"
        )
        convention2 = self.clone_convention(convention)
        convention2.numero = "13.67890.23.0001"
        convention2.statut = ConventionStatut.A_SIGNER
        convention2.valide_le = datetime.date.today()
        convention2.save()

        self.assertEqual(
            convention.get_convention_prefix(), f"13.67890.{current_year}.0002"
        )
        convention3 = self.clone_convention(convention)
        convention3.numero = "13.67890.23.9998"
        convention3.statut = ConventionStatut.A_SIGNER
        convention3.valide_le = datetime.date.today()
        convention3.save()
        self.assertEqual(
            convention.get_convention_prefix(), f"13.67890.{current_year}.9999"
        )

    def test_get_convention_prefix_different_admin(self):
        current_year = datetime.date.today().year % 100
        convention = Convention.objects.order_by("uuid").first()
        self.assertEqual(
            convention.get_convention_prefix(), f"13.67890.{current_year}.0001"
        )
        convention2 = self.clone_convention(convention)
        convention2.numero = "13.D.23.0001"
        convention2.statut = ConventionStatut.A_SIGNER
        convention2.valide_le = datetime.date.today()
        convention2.save()
        self.assertEqual(
            convention.get_convention_prefix(), f"13.67890.{current_year}.0002"
        )


class ConventionHistoryModelsTest(TestCase):
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

    def test_email_survey_for_bailleur(self):
        convention = Convention.objects.all().order_by("uuid").first()
        bailleur = User.objects.filter(roles__typologie=TypeRole.BAILLEUR).first()
        with mock.patch(
            "core.services.EmailService.send_transactional_email"
        ) as mock_send_email:
            for convention_statut in [
                ConventionStatut.A_SIGNER.label,
                ConventionStatut.A_SIGNER.label,
                ConventionStatut.INSTRUCTION.label,
                ConventionStatut.INSTRUCTION.label,
            ]:
                ConventionHistory.objects.create(
                    convention=convention,
                    statut_convention=convention_statut,
                    user=bailleur,
                )
            mock_send_email.assert_called_once_with(
                email_data={
                    "email": bailleur.email,
                    "firstname": bailleur.first_name,
                    "lastname": bailleur.last_name,
                }
            )

    def test_email_survey_for_intructeur(self):
        convention = Convention.objects.all().order_by("uuid").first()
        instructeur = User.objects.filter(roles__typologie=TypeRole.INSTRUCTEUR).first()

        with mock.patch(
            "core.services.EmailService.send_transactional_email"
        ) as mock_send_email:
            for convention_statut in [
                ConventionStatut.A_SIGNER.label,
                ConventionStatut.A_SIGNER.label,
                ConventionStatut.INSTRUCTION.label,
                ConventionStatut.INSTRUCTION.label,
            ]:
                ConventionHistory.objects.create(
                    convention=convention,
                    statut_convention=convention_statut,
                    user=instructeur,
                )
            mock_send_email.assert_called_once_with(
                email_data={
                    "email": instructeur.email,
                    "firstname": instructeur.first_name,
                    "lastname": instructeur.last_name,
                }
            )


@pytest.mark.django_db
class TestConventionSignals:

    def test_numero_pour_recherche_create_num_none(self):
        convention = ConventionFactory(numero=None)

        assert convention.numero is None
        assert convention.numero_pour_recherche is None

    def test_numero_pour_recherche_create_num_alphanum(self):
        convention = ConventionFactory(numero="ALPHA1230")

        assert convention.numero == "ALPHA1230"
        assert convention.numero == convention.numero_pour_recherche

    def test_numero_pour_recherche_create_with_special_char(self):
        convention = ConventionFactory(numero="ALPHA/1-2.3 0")

        assert convention.numero == "ALPHA/1-2.3 0"
        assert convention.numero_pour_recherche == "ALPHA1230"

    def test_numero_pour_recherche_create_num_update(self):
        convention = ConventionFactory()

        convention.numero = "ALPHA1230"
        convention.save()

        assert convention.numero == "ALPHA1230"
        assert convention.numero == convention.numero_pour_recherche

        convention.numero = "ALPHA/1-2.3 0"
        convention.save()

        assert convention.numero == "ALPHA/1-2.3 0"
        assert convention.numero_pour_recherche == "ALPHA1230"


def test_convention_date_signature_choices():
    current_year = datetime.date.today().year
    choices = Convention.date_signature_choices(from_threshold=True)
    assert choices[0] == (current_year, str(current_year))
    assert choices[-1] == (1900, "1900")
