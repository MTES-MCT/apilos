from django.db import models


class Zone123(models.TextChoices):
    Zone1 = "1", "01"
    Zone2 = "2", "02"
    Zone3 = "3", "03"
    Zone1bis = "1bis", "1bis"


class ZoneABC(models.TextChoices):
    ZoneA = "A", "A"
    ZoneAbis = "Abis", "Abis"
    ZoneB1 = "B1", "B1"
    ZoneB2 = "B2", "B2"
    ZoneC = "C", "C"
    DROM = "DROM", "DROM"


class Financement(models.TextChoices):
    PLUS = "PLUS", "PLUS"
    PLUS_CD = "PLUS_CD", "PLUS_CD"
    PLAI = "PLAI", "PLAI"
    PLAI_ADP = "PLAI_ADP", "PLAI_ADP"
    PLUS_PLAI = "PLUS-PLAI", "PLUS-PLAI"
    PLS = "PLS", "PLS"
    PSH = "PSH", "PSH"
    PALULOS = "PALULOS", "PALULOS"
    SANS_FINANCEMENT = "SANS_FINANCEMENT", "Sans Financement"
    # Financements spécifiques outre-mer
    LLS = "LLS", "LLS"
    LLTS = "LLTS", "LLTS"
    LLTSA = "LLTSA", "LLTSA"
    PLS_DOM = "PLS_DOM", "PLS_DOM"
    SALLS_R = "SALLS_R", "SALLS Réhabiliation"
    # Financement spécifique Seconde vie
    SECD_VIE = "SECD_VIE", "SECD_VIE"


class FinancementEDD(models.TextChoices):
    PLUS = "PLUS", "PLUS"
    PLUS_CD = "PLUS_CD", "PLUS_CD"
    PLAI = "PLAI", "PLAI"
    PLS = "PLS", "PLS"
    SANS_FINANCEMENT = "SANS_FINANCEMENT", "Sans Financement"


class TypologieLogementClassique(models.TextChoices):
    T1 = "T1", "T1"
    T1BIS = "T1bis", "T1 bis"
    T1prime = "T1prime", "T1'"
    T2 = "T2", "T2"
    T3 = "T3", "T3"
    T4 = "T4", "T4"
    T5 = "T5", "T5"
    T6 = "T6", "T6 et plus"


class TypologieLogementFoyerResidence(models.TextChoices):
    T1 = "T1", "T1"
    T1BIS = "T1bis", "T1 bis"
    T1prime = "T1prime", "T1'"
    T2 = "T2", "T2"
    T3 = "T3", "T3"
    T4 = "T4", "T4"
    T5 = "T5", "T5"
    T6 = "T6", "T6"
    T7 = "T7", "T7"


class TypologieLogement(models.TextChoices):
    T1 = "T1", "T1"
    T1BIS = "T1bis", "T1 bis"
    T1prime = "T1prime", "T1'"
    T2 = "T2", "T2"
    T3 = "T3", "T3"
    T4 = "T4", "T4"
    T5 = "T5", "T5"
    T6 = "T6", "T6"
    T7 = "T7", "T7"

    @classmethod
    def map_string(cls, value):
        mapping = {
            "1": "T1",
            "1bis": "T1 bis",
            "1 bis": "T1 bis",
            "T1bis": "T1 bis",
            "2": "T2",
            "3": "T3",
            "4": "T4",
            "5": "T5",
            "5 et plus": "T5",
            "T5 et plus": "T5",
            "T6": "T6",
            "6": "T6",
            "6 et plus": "T6",
            "T6 et plus": "T6",
            "7": "T7",
        }
        value = str(value)
        if value in mapping:
            return mapping[value]
        return value


class ActiveNatureLogement(models.TextChoices):
    LOGEMENTSORDINAIRES = "LOGEMENTSORDINAIRES", "Logements ordinaires"
    AUTRE = "AUTRE", "Autres logements foyers (Convention de type Foyer)"
    HEBERGEMENT = "HEBERGEMENT", "Hébergement (Convention de type Résidence)"
    RESISDENCESOCIALE = (
        "RESISDENCESOCIALE",
        "Résidence sociale (Convention de type Résidence)",
    )
    PENSIONSDEFAMILLE = (
        "PENSIONSDEFAMILLE",
        "Pensions de famille, maisons relais (Convention de type Résidence)",
    )
    RESIDENCEDACCUEIL = (
        "RESIDENCEDACCUEIL",
        "Résidence d'accueil (Convention de type Résidence)",
    )
    RESIDENCEUNIVERSITAIRE = "RESIDENCEUNIVERSITAIRE", "Résidence universitaire"


class NatureLogement(models.TextChoices):
    LOGEMENTSORDINAIRES = "LOGEMENTSORDINAIRES", "Logements ordinaires"
    AUTRE = "AUTRE", "Autres logements foyers"
    HEBERGEMENT = "HEBERGEMENT", "Hébergement"
    RESISDENCESOCIALE = "RESISDENCESOCIALE", "Résidence sociale"
    PENSIONSDEFAMILLE = "PENSIONSDEFAMILLE", "Pensions de famille (Maisons relais)"
    RESIDENCEDACCUEIL = "RESIDENCEDACCUEIL", "Résidence d'accueil"
    RESIDENCEUNIVERSITAIRE = "RESIDENCEUNIVERSITAIRE", "Résidence universitaire"
    RHVS = "RHVS", "RHVS"

    @classmethod
    def eligible_for_update(cls):
        return [
            cls.LOGEMENTSORDINAIRES,
            cls.RESISDENCESOCIALE,
            cls.RESIDENCEDACCUEIL,
            cls.AUTRE,
        ]


class TypeOperation(models.TextChoices):
    SANSOBJET = "SANSOBJET", "Sans Objet"
    NEUF = "NEUF", "Construction Neuve"
    VEFA = "VEFA", "Construction Neuve > VEFA"
    ACQUIS = "ACQUIS", "Acquisition"
    ACQUISAMELIORATION = "ACQUISAMELIORATION", "Acquisition-Amélioration"
    REHABILITATION = "REHABILITATION", "Réhabilitation"
    ACQUISSANSTRAVAUX = "ACQUISSANSTRAVAUX", "Acquisition sans travaux"
    SANSTRAVAUX = "SANSTRAVAUX", "Sans aide financière (sans travaux)"
    USUFRUIT = "USUFRUIT", "Usufruit"


class TypeHabitat(models.TextChoices):
    MIXTE = "MIXTE", "Mixte"
    INDIVIDUEL = "INDIVIDUEL", "Individuel"
    COLLECTIF = "COLLECTIF", "Collectif"


class TypologieAnnexe(models.TextChoices):
    TERRASSE = "TERRASSE", "Terrasse"
    JARDIN = "JARDIN", "Jardin"
    COUR = "COUR", "Cour"


class TypologieStationnement(models.TextChoices):
    GARAGE_AERIEN = "GARAGE_AERIEN", "Garage aérien"
    GARAGE_ENTERRE = "GARAGE_ENTERRE", "Garage enterré"
    PLACE_STATIONNEMENT = "PLACE_STATIONNEMENT", "Place de stationnement"
    PARKING_EXTERIEUR_PRIVATIF = (
        "PARKING_EXTERIEUR_PRIVATIF",
        "Parking extérieur privatif",
    )
    PARKING_SOUSSOL = "PARKING_SOUSSOL", "Parking en sous-sol ou en superstructure"
    GARAGE_BOXE_SIMPLE = "GARAGE_BOXE_SIMPLE", "Garage boxé simple"
    GARAGE_BOXE_DOUBLE = "GARAGE_BOXE_DOUBLE", "Garage boxé double"
    EXTERIEUR_BOXE = "EXTERIEUR_BOXE", "extérieur boxé"
    SOUSSOL_BOXE = "SOUSSOL_BOXE", "en sous-sol boxé"
    CARPORT = "CARPORT", "Carport"
    DEUX_ROUES_EXTERIEUR = "DEUX_ROUES_EXTERIEUR", "2 roues en extérieur"
    DEUX_ROUES_SOUSSOL = "DEUX_ROUES_SOUSSOL", "2 roues en sous-sol"
    DOUBLE_SOUSSOL = "DOUBLE_SOUSSOL", "Parking double en sous-sol"
    DOUBLE_SUPERSTRUCTURE = "DOUBLE_SUPERSTRUCTURE", "Parking double en superstructure"
    INDIVIDUEL_JUMELES_PAR_2 = (
        "INDIVIDUEL_JUMELES_PAR_2",
        "Garages individuels jumelés par blocs de 2",
    )
    PLACE_PARKING_ACCOLEE = (
        "PLACE_PARKING_ACCOLEE",
        "Place de parking accolée à chaque garage",
    )
