import json
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse

from conventions.services.alertes import ALERTE_CATEGORY_MAPPING, AlerteService
from core.tests.factories import ConventionFactory
from siap.siap_client.client import SIAPClient


@pytest.fixture
def siap_credentials():
    return {"habilitation_id": "001", "user_login": 1}


@pytest.fixture
def alerte_service(siap_credentials):
    convention = ConventionFactory()
    return AlerteService(convention=convention, siap_credentials=siap_credentials)


@pytest.fixture
def avenant_alerte_service(siap_credentials):
    convention = ConventionFactory()
    avenant = ConventionFactory(parent_id=convention.id)
    return AlerteService(convention=avenant, siap_credentials=siap_credentials)


@pytest.mark.django_db
def test_create_alertes_instruction(alerte_service, avenant_alerte_service):
    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = MagicMock()
        mock_get_instance.return_value = mock_client
        alerte_service.create_alertes_instruction()
        mock_client.create_alerte.assert_called()
        payload_bailleur = json.loads(
            mock_client.create_alerte.mock_calls[0].kwargs["payload"]
        )
        assert payload_bailleur["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "MO"}
        ]
        assert payload_bailleur["etiquettePersonnalisee"] == "Convention en instruction"
        assert (
            payload_bailleur["categorieInformation"]
            == ALERTE_CATEGORY_MAPPING["information"]
        )
        assert payload_bailleur["urlDirection"] == reverse(
            "conventions:recapitulatif", args=[alerte_service.convention.uuid]
        )

        payload_instructeur = json.loads(
            mock_client.create_alerte.mock_calls[1].kwargs["payload"]
        )
        assert payload_instructeur["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "SG"}
        ]
        assert payload_instructeur["etiquettePersonnalisee"] == "Convention à instruire"
        assert (
            payload_instructeur["categorieInformation"]
            == ALERTE_CATEGORY_MAPPING["action"]
        )
        assert payload_instructeur["urlDirection"] == reverse(
            "conventions:recapitulatif", args=[alerte_service.convention.uuid]
        )

        avenant_alerte_service.create_alertes_instruction()
        payload_bailleur = json.loads(
            mock_client.create_alerte.mock_calls[2].kwargs["payload"]
        )
        assert payload_bailleur["etiquettePersonnalisee"] == "Avenant en instruction"
        payload_instructeur = json.loads(
            mock_client.create_alerte.mock_calls[3].kwargs["payload"]
        )
        assert payload_instructeur["etiquettePersonnalisee"] == "Avenant à instruire"


@pytest.mark.django_db
def test_create_alertes_correction_from_instructeur(
    alerte_service, avenant_alerte_service
):
    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = MagicMock()
        mock_get_instance.return_value = mock_client
        alerte_service.create_alertes_correction(from_instructeur=True)
        mock_client.create_alerte.assert_called()

        payload_information = json.loads(
            mock_client.create_alerte.mock_calls[0].kwargs["payload"]
        )
        assert payload_information["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "SG"}
        ]
        assert (
            payload_information["etiquettePersonnalisee"] == "Convention en correction"
        )
        assert (
            payload_information["categorieInformation"]
            == ALERTE_CATEGORY_MAPPING["information"]
        )
        assert payload_information["urlDirection"] == reverse(
            "conventions:recapitulatif", args=[alerte_service.convention.uuid]
        )

        payload_action = json.loads(
            mock_client.create_alerte.mock_calls[1].kwargs["payload"]
        )
        assert payload_action["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "MO"}
        ]
        assert payload_action["etiquettePersonnalisee"] == "Convention à corriger"
        assert (
            payload_action["categorieInformation"] == ALERTE_CATEGORY_MAPPING["action"]
        )
        assert payload_action["urlDirection"] == reverse(
            "conventions:recapitulatif", args=[alerte_service.convention.uuid]
        )

        avenant_alerte_service.create_alertes_correction(from_instructeur=True)
        payload_information = json.loads(
            mock_client.create_alerte.mock_calls[2].kwargs["payload"]
        )
        assert payload_information["etiquettePersonnalisee"] == "Avenant en correction"
        payload_action = json.loads(
            mock_client.create_alerte.mock_calls[3].kwargs["payload"]
        )
        assert payload_action["etiquettePersonnalisee"] == "Avenant à corriger"


@pytest.mark.django_db
def test_create_alertes_correction_from_bailleur(
    alerte_service, avenant_alerte_service
):
    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = MagicMock()
        mock_get_instance.return_value = mock_client
        alerte_service.create_alertes_correction(from_instructeur=False)
        mock_client.create_alerte.assert_called()

        payload_information = json.loads(
            mock_client.create_alerte.mock_calls[0].kwargs["payload"]
        )
        assert payload_information["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "MO"}
        ]
        assert (
            payload_information["etiquettePersonnalisee"] == "Convention en instruction"
        )
        assert (
            payload_information["categorieInformation"]
            == ALERTE_CATEGORY_MAPPING["information"]
        )

        payload_action = json.loads(
            mock_client.create_alerte.mock_calls[1].kwargs["payload"]
        )
        assert payload_action["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "SG"}
        ]
        assert (
            payload_action["etiquettePersonnalisee"]
            == "Convention à instruire à nouveau"
        )
        assert (
            payload_action["categorieInformation"] == ALERTE_CATEGORY_MAPPING["action"]
        )

        avenant_alerte_service.create_alertes_correction(from_instructeur=False)
        payload_information = json.loads(
            mock_client.create_alerte.mock_calls[2].kwargs["payload"]
        )
        assert payload_information["etiquettePersonnalisee"] == "Avenant en instruction"
        payload_action = json.loads(
            mock_client.create_alerte.mock_calls[3].kwargs["payload"]
        )
        assert (
            payload_action["etiquettePersonnalisee"] == "Avenant à instruire à nouveau"
        )


@pytest.mark.django_db
def test_create_alertes_valide(alerte_service, avenant_alerte_service):
    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = MagicMock()
        mock_get_instance.return_value = mock_client
        alerte_service.create_alertes_valide()
        mock_client.create_alerte.assert_called()
        payload_bailleur = json.loads(
            mock_client.create_alerte.mock_calls[0].kwargs["payload"]
        )
        assert payload_bailleur["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "MO"}
        ]
        assert (
            payload_bailleur["etiquettePersonnalisee"] == "Convention validée à signer"
        )
        assert (
            payload_bailleur["categorieInformation"]
            == ALERTE_CATEGORY_MAPPING["action"]
        )

        assert payload_bailleur["urlDirection"] == reverse(
            "conventions:preview", args=[alerte_service.convention.uuid]
        )

        payload_instructeur = json.loads(
            mock_client.create_alerte.mock_calls[1].kwargs["payload"]
        )
        assert payload_instructeur["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "SG"}
        ]
        assert (
            payload_instructeur["etiquettePersonnalisee"]
            == "Convention validée à signer"
        )
        assert (
            payload_instructeur["categorieInformation"]
            == ALERTE_CATEGORY_MAPPING["action"]
        )
        assert payload_instructeur["urlDirection"] == reverse(
            "conventions:preview", args=[alerte_service.convention.uuid]
        )

        avenant_alerte_service.create_alertes_valide()
        payload_bailleur = json.loads(
            mock_client.create_alerte.mock_calls[2].kwargs["payload"]
        )
        assert payload_bailleur["etiquettePersonnalisee"] == "Avenant validé à signer"
        payload_instructeur = json.loads(
            mock_client.create_alerte.mock_calls[3].kwargs["payload"]
        )
        assert (
            payload_instructeur["etiquettePersonnalisee"] == "Avenant validé à signer"
        )


@pytest.mark.django_db
def test_create_alertes_publication_en_cours(alerte_service):
    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = MagicMock()
        mock_get_instance.return_value = mock_client
        alerte_service.create_alertes_publication_en_cours()
        mock_client.create_alerte.assert_called_once()
        payload = json.loads(mock_client.create_alerte.mock_calls[0].kwargs["payload"])
        assert payload["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "SG"},
        ]
        assert payload["etiquettePersonnalisee"] == "Convention en cours de publication"
        assert payload["categorieInformation"] == ALERTE_CATEGORY_MAPPING["information"]

        assert payload["urlDirection"] == reverse(
            "conventions:recapitulatif", args=[alerte_service.convention.uuid]
        )


@pytest.mark.django_db
def test_create_alertes_publie(alerte_service):
    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = MagicMock()
        mock_get_instance.return_value = mock_client
        alerte_service.create_alertes_publie()
        mock_client.create_alerte.assert_called_once()
        payload = json.loads(mock_client.create_alerte.mock_calls[0].kwargs["payload"])
        assert payload["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "SG"},
        ]
        assert payload["etiquettePersonnalisee"] == "Convention publiée"
        assert payload["categorieInformation"] == ALERTE_CATEGORY_MAPPING["information"]

        assert payload["urlDirection"] == reverse(
            "conventions:recapitulatif", args=[alerte_service.convention.uuid]
        )


@pytest.mark.django_db
def test_create_alertes_signed(alerte_service, avenant_alerte_service):
    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = MagicMock()
        mock_get_instance.return_value = mock_client
        alerte_service.create_alertes_signed()
        mock_client.create_alerte.assert_called_once()
        payload = json.loads(mock_client.create_alerte.mock_calls[0].kwargs["payload"])
        assert payload["destinataires"] == [
            {"role": "INSTRUCTEUR", "service": "MO"},
            {"role": "INSTRUCTEUR", "service": "SG"},
        ]
        assert payload["etiquettePersonnalisee"] == "Convention signée"
        assert payload["categorieInformation"] == ALERTE_CATEGORY_MAPPING["information"]

        assert payload["urlDirection"] == reverse(
            "conventions:preview", args=[alerte_service.convention.uuid]
        )

        avenant_alerte_service.create_alertes_signed()
        payload = json.loads(mock_client.create_alerte.mock_calls[1].kwargs["payload"])
        assert payload["etiquettePersonnalisee"] == "Avenant signé"


@pytest.mark.django_db
def test_delete_action_alertes(alerte_service):
    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = MagicMock()
        mock_get_instance.return_value = mock_client
        mock_client.list_convention_alertes.return_value = [
            {"id": 1, "categorie": ALERTE_CATEGORY_MAPPING["action"]},
            {"id": 2, "categorie": ALERTE_CATEGORY_MAPPING["information"]},
        ]
        alerte_service.delete_action_alertes()

        mock_client.delete_alerte.assert_called_once()
        assert mock_client.delete_alerte.mock_calls[0].kwargs["alerte_id"] == 1
