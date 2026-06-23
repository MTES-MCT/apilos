from django.test import TestCase
from django.urls import reverse

from bailleurs.models import NatureBailleur
from conventions.tests.views.abstract import AbstractEditViewTestCase
from programmes.models import NatureLogement


class ConventionCadastreViewTests(AbstractEditViewTestCase, TestCase):
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

    def setUp(self):
        super().setUp()

        self.target_path = reverse(
            "conventions:cadastre", args=[self.convention_75.uuid]
        )
        # Default: use AUTRE (foyer) so next step is EDD
        self.convention_75.programme.nature_logement = NatureLogement.AUTRE
        self.convention_75.programme.save()
        self.next_target_path = reverse(
            "conventions:edd", args=[self.convention_75.uuid]
        )

        self.target_template = "conventions/cadastre.html"
        self.error_payload = {
            "permis_construire": "",
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 0,
            "form-0-uuid": "",
            "form-0-section": "",
            "form-0-numero": "13",
            "form-0-lieudit": "Marseille",
            "form-0-surface": "0 ha 1 a 27 ca",
            "form-1-uuid": "",
            "form-1-section": "AC",
            "form-1-numero": "15",
            "form-1-lieudit": "Marseille",
            "form-1-surface": "0 ha 1 a 2 ca",
            "effet_relatif_files": "{}",
            "acte_de_propriete_files": "{}",
            "certificat_adressage_files": "{}",
        }
        self.success_payload = {
            "permis_construire": "",
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 0,
            "form-0-uuid": "",
            "form-0-section": "AC",
            "form-0-numero": "13",
            "form-0-lieudit": "Marseille",
            "form-0-surface": "0 ha 1 a 27 ca",
            "form-1-uuid": "",
            "form-1-section": "AC",
            "form-1-numero": "15",
            "form-1-lieudit": "Marseille",
            "form-1-surface": "0 ha 1 a 2 ca",
            "effet_relatif_files": "{}",
            "acte_de_propriete_files": "{}",
            "certificat_adressage_files": "{}",
        }
        self.msg_prefix = "[ConventionCadastreViewTests] "

    def _test_data_integrity(self):
        pass

    def _set_properties_and_post(self, **kwargs):
        """Helper: set nature_logement, save, login, POST success_payload."""
        if "nature_logement" in kwargs:
            self.convention_75.programme.nature_logement = kwargs["nature_logement"]
            self.convention_75.programme.save()
        if "type_bailleur" in kwargs:
            self.convention_75.programme.bailleur.nature_bailleur = kwargs[
                "type_bailleur"
            ]
            self.convention_75.programme.bailleur.save()

        self.client.login(username="nicolas", password="12345")
        return self.client.post(self.target_path, self.success_payload)

    def test_next_step_is_financement_for_residence_universitaire(self):
        response = self._set_properties_and_post(
            nature_logement=NatureLogement.RESIDENCEUNIVERSITAIRE
        )
        expected = reverse("conventions:edd", args=[self.convention_75.uuid])
        self.assertRedirects(response, expected)

    def test_next_step_is_financement_for_hebergement(self):
        response = self._set_properties_and_post(
            nature_logement=NatureLogement.HEBERGEMENT
        )
        expected = reverse("conventions:financement", args=[self.convention_75.uuid])
        self.assertRedirects(response, expected)

    def test_next_step_is_financement_for_residence_sociale(self):
        response = self._set_properties_and_post(
            nature_logement=NatureLogement.RESISDENCESOCIALE
        )
        expected = reverse("conventions:financement", args=[self.convention_75.uuid])
        self.assertRedirects(response, expected)

    def test_next_step_is_financement_for_pensions_de_famille(self):
        response = self._set_properties_and_post(
            nature_logement=NatureLogement.PENSIONSDEFAMILLE
        )
        expected = reverse("conventions:financement", args=[self.convention_75.uuid])
        self.assertRedirects(response, expected)

    def test_next_step_is_financement_for_residence_accueil(self):
        response = self._set_properties_and_post(
            nature_logement=NatureLogement.RESIDENCEDACCUEIL
        )
        expected = reverse("conventions:financement", args=[self.convention_75.uuid])
        self.assertRedirects(response, expected)

    def test_next_step_is_financement_for_logements_ordinaires_bailleur_is_hlm(self):
        response = self._set_properties_and_post(
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            type_bailleur=NatureBailleur.HLM,
        )
        expected = reverse("conventions:financement", args=[self.convention_75.uuid])
        self.assertRedirects(response, expected)

    def test_next_step_is_financement_for_logements_ordinaires_bailleur_is_sem(self):
        response = self._set_properties_and_post(
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            type_bailleur=NatureBailleur.SEM,
        )
        expected = reverse("conventions:financement", args=[self.convention_75.uuid])
        self.assertRedirects(response, expected)

    def test_next_step_is_financement_for_logements_ordinaires_bailleur_is_type_1_2(
        self,
    ):
        response = self._set_properties_and_post(
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES
        )
        expected = reverse("conventions:edd", args=[self.convention_75.uuid])
        self.assertRedirects(response, expected)

    def test_next_step_is_edd_for_rhvs(self):
        response = self._set_properties_and_post(nature_logement=NatureLogement.RHVS)
        expected = reverse("conventions:edd", args=[self.convention_75.uuid])
        self.assertRedirects(response, expected)

    def test_next_step_is_edd_for_autre(self):
        response = self._set_properties_and_post(nature_logement=NatureLogement.AUTRE)
        expected = reverse("conventions:edd", args=[self.convention_75.uuid])
        self.assertRedirects(response, expected)
