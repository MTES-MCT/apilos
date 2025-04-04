from dataclasses import dataclass, field
from datetime import date

# create dataclass from CreationAlerteApilosDTO.properties
from typing import Literal

from dataclasses_json import LetterCase, config, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Destinataire:
    nom: str
    email: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreationAlerte:
    module: str = field(init=False)

    # Catégorie d'alerte (INFORMATION, MODIFICATION, ACTION)
    categorie_information: Literal[
        "CATEGORIE_ALERTE_INFORMATION",
        "CATEGORIE_ALERTE_ACTION",
        "CATEGORIE_ALERTE_MODIFICATION",
    ]

    code_commune: str  # code insee commune
    code_gestion: str  # code de gestion du service gestionnaire

    # date de création de l'alerte
    date_creation: date = field(
        metadata=config(encoder=date.isoformat, decoder=date.fromisoformat)
    )

    destinataires: list[Destinataire]  # liste des destinataires de l'alerte

    # étiquette de l'alerte
    etiquette: Literal[
        "VALIDATION_DELEGATAIRE",
        "DEMANDE_VALIDATION_DELEGATAIRE",
        "A_TRANSMETTRE",
        "A_REVOIR",
        "A_PROGRAMMER",
        "PROG_REFUSEE",
        "PROGRAMMEE",
        "RE_PROGRAMMATION",
        "PROP_AGREMENT_A_VALIDER",
        "PROP_AGREMENT_REFUSEE",
        "PROP_AGREMENT",
        "A_COMPLETER",
        "AGREMENT_A_VALIDER",
        "AGREMENT_REFUSE",
        "AGREMENT_A_SIGNER",
        "DATE_SIGNATURE_MODIFIEE",
        "DECISION_REMPLACEE",
        "SIGNATURE_REFUSE",
        "SIGNE",
        "EJ_A_GENERER",
        "CLOTURE_A_APPROUVER",
        "DEMANDE_CLOTURE_NON_APPROUVEE",
        "DEMANDE_CLOTURE",
        "DEMANDE_CLOTURE_REFUSEE",
        "CLOTURE_A_VALIDER",
        "CLOTURE_REFUSEE",
        "CLOTURE_A_SIGNER",
        "SIGNATURE_CLOTURE_REFUSEEE",
        "CLOTUREE",
        "SOLDEE",
        "SUPPRIMER_OPERATION",
        "ACOMPTE_A_APPROUVER",
        "ACOMPTE_NON_APPROUVE",
        "NOUVEAU_ACOMPTE",
        "ACOMPTE_REFUSE",
        "ACOMPTE_A_VALIDER",
        "ACOMPTE_A_VALIDER_REFUSE",
        "ACOMPTE_A_SIGNER",
        "ACOMPTE_A_SIGNER_REFUSE",
        "ACOMPTE_A_ENVOYER",
        "ACOMPTE_SIGNE",
        "ACOMPTE_VERSE",
        "PJ_COMPROMISE",
        "PJ_REFUSEE",
        "PROROGATION_A_INSTRUIRE",
        "PROROGATION_VALIDEE",
        "PROROGATION_REFUSEE",
        "DEROGATION_A_INSTRUIRE",
        "DEROGATION_VALIDEE",
        "DEROGATION_REFUSEE",
        "ANNULATION_DECISION_AGREMENT",
        "ANNULATION_OPERATION",
        "DECISION_CONFIRMATION_A_VALIDER_MO",
        "DECISION_CONFIRMATION_REFUSEE_MO",
        "DECISION_CONFIRMATION_REFUSEE_SG_MO",
        "DECISION_CONFIRMATION_REFUSEE_SG_SG",
        "DECISION_CONFIRMATION_A_CONFIRMER_SG",
        "DECISION_CONFIRMATION_A_VALIDER_SG",
        "DECISION_CONFIRMATION_A_SIGNER_SG",
        "DECISION_CONFIRMATION_ANNULATION_A_SIGNER_SG",
        "DECISION_CONFIRMATION_CONFIRMEE",
        "DECISION_CONFIRMATION_ANNULEE",
        "NOT_PAI",
        "CUSTOM",
    ]

    etiquette_personnalisee: str  # étiquette personnalisée

    nom_operation: str  # nom de l'opération liée à l'alerte
    num_operation: str  # numéro de l'opération liée à l'alerte
    num_convention: str  # numéro de la convention liée à l'alerte

    id_convention: str  # ID de convention liée à l'alerte
    siren: str  # SIREN du maître d'ouvrage
    type_alerte: str  # type d'alerte
    url_direction: str  # URL de redirection

    def __post_init__(self):
        self.module = "APILOS"
