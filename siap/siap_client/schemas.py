from dataclasses import dataclass, field
from datetime import date

# create dataclass from CreationAlerteApilosDTO.properties
from typing import TYPE_CHECKING, Literal, Self

from dataclasses_json import LetterCase, config, dataclass_json

if TYPE_CHECKING:
    from conventions.models import Convention


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Destinataire:
    role: Literal["INSTRUCTEUR", "VALIDEUR", "ADMINISTRATEUR"]
    service: Literal["MO", "SG"]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Alerte:
    module: str = field(init=False)
    date_creation: date = field(
        metadata=config(encoder=date.isoformat, decoder=date.fromisoformat),
        init=False,
    )

    # Catégorie d'alerte (INFORMATION, MODIFICATION, ACTION)
    categorie_information: Literal[
        "CATEGORIE_ALERTE_INFORMATION",
        "CATEGORIE_ALERTE_ACTION",
        "CATEGORIE_ALERTE_MODIFICATION",
    ]

    destinataires: list[Destinataire]  # liste des destinataires de l'alerte

    # étiquette de l'alerte
    etiquette: Literal[
        "A_COMPLETER",
        "A_PROGRAMMER",
        "A_REVOIR",
        "A_TRANSMETTRE",
        "ACOMPTE_A_APPROUVER",
        "ACOMPTE_A_ENVOYER",
        "ACOMPTE_A_SIGNER_REFUSE",
        "ACOMPTE_A_SIGNER",
        "ACOMPTE_A_VALIDER_REFUSE",
        "ACOMPTE_A_VALIDER",
        "ACOMPTE_NON_APPROUVE",
        "ACOMPTE_REFUSE",
        "ACOMPTE_SIGNE",
        "ACOMPTE_VERSE",
        "AGREMENT_A_SIGNER",
        "AGREMENT_A_VALIDER",
        "AGREMENT_REFUSE",
        "ANNULATION_DECISION_AGREMENT",
        "ANNULATION_OPERATION",
        "CLOTURE_A_APPROUVER",
        "CLOTURE_A_SIGNER",
        "CLOTURE_A_VALIDER",
        "CLOTURE_REFUSEE",
        "CLOTUREE",
        "CUSTOM",
        "DATE_SIGNATURE_MODIFIEE",
        "DECISION_CONFIRMATION_A_CONFIRMER_SG",
        "DECISION_CONFIRMATION_A_SIGNER_SG",
        "DECISION_CONFIRMATION_A_VALIDER_MO",
        "DECISION_CONFIRMATION_A_VALIDER_SG",
        "DECISION_CONFIRMATION_ANNULATION_A_SIGNER_SG",
        "DECISION_CONFIRMATION_ANNULEE",
        "DECISION_CONFIRMATION_CONFIRMEE",
        "DECISION_CONFIRMATION_REFUSEE_MO",
        "DECISION_CONFIRMATION_REFUSEE_SG_MO",
        "DECISION_CONFIRMATION_REFUSEE_SG_SG",
        "DECISION_REMPLACEE",
        "DEMANDE_CLOTURE_NON_APPROUVEE",
        "DEMANDE_CLOTURE_REFUSEE",
        "DEMANDE_CLOTURE",
        "DEMANDE_VALIDATION_DELEGATAIRE",
        "DEROGATION_A_INSTRUIRE",
        "DEROGATION_REFUSEE",
        "DEROGATION_VALIDEE",
        "EJ_A_GENERER",
        "NOT_PAI",
        "NOUVEAU_ACOMPTE",
        "PJ_COMPROMISE",
        "PJ_REFUSEE",
        "PROG_REFUSEE",
        "PROGRAMMEE",
        "PROP_AGREMENT_A_VALIDER",
        "PROP_AGREMENT_REFUSEE",
        "PROP_AGREMENT",
        "PROROGATION_A_INSTRUIRE",
        "PROROGATION_REFUSEE",
        "PROROGATION_VALIDEE",
        "RE_PROGRAMMATION",
        "SIGNATURE_CLOTURE_REFUSEEE",
        "SIGNATURE_REFUSE",
        "SIGNE",
        "SOLDEE",
        "SUPPRIMER_OPERATION",
        "VALIDATION_DELEGATAIRE",
    ]

    etiquette_personnalisee: str  # étiquette personnalisée
    type_alerte: str  # type d'alerte
    url_direction: str  # URL de redirection

    id_convention: str  # ID de convention liée à l'alerte
    num_convention: str  # numéro de la convention liée à l'alerte

    code_commune: str  # code insee commune
    code_gestion: str  # code de gestion du service gestionnaire
    nom_operation: str  # nom de l'opération liée à l'alerte
    num_operation: str  # numéro de l'opération liée à l'alerte
    siren: str  # SIREN du maître d'ouvrage

    def __post_init__(self):
        self.module = "APILOS"
        self.date_creation = date.today()

    @classmethod
    def from_convention(cls, convention: "Convention", **kwargs) -> Self:
        return cls(
            code_commune=convention.programme.code_insee_commune,
            code_gestion=convention.programme.administration.code,
            id_convention=str(convention.uuid),
            num_convention=convention.numero,
            nom_operation=convention.programme.nom,
            num_operation=convention.programme.numero_operation,
            siren=convention.programme.bailleur.siren,
            **kwargs,
        )
