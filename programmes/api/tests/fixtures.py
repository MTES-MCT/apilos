bailleur = {
    "nom": "3F",
    "siren": "123456789",
    "siret": "12345678901234",
    "adresse": None,
    "code_postal": None,
    "ville": "Marseille",
    "capital_social": 123000.5,
    "sous_nature_bailleur": "NONRENSEIGNE",
}
administration = {
    "nom": "CA d'Arles-Crau-Camargue-Montagnette",
    "code": "12345",
    "ville_signature": None,
}
programme1 = {
    "nom": "Programme 1",
    "code_postal": "75007",
    "ville": "Paris",
    "adresse": "22 rue segur",
    "numero_galion": "20220600005",
    "zone_123": "3",
    "zone_abc": "B1",
    "type_operation": "NEUF",
    "anru": False,
    "date_achevement_previsible": "2024-01-02",
    "date_achat": "2022-01-02",
    "date_achevement": "2024-04-11",
}
programme2 = {
    "nom": "Programme 2",
    "code_postal": "13010",
    "ville": "Marseille",
    "adresse": "Rue Francois Mauriac ",
    "numero_galion": "20220600006",
    "zone_123": "A",
    "zone_abc": "02",
    "type_operation": "NEUF",
    "anru": False,
    "date_achevement_previsible": None,
    "date_achat": None,
    "date_achevement": None,
}

logts1 = [
    {
        "designation": "PLUS 1",
        "typologie": "T1",
        "surface_habitable": "50.00",
        "surface_annexes": "20.00",
        "surface_annexes_retenue": "10.00",
        "surface_utile": "60.00",
        "loyer_par_metre_carre": "5.50",
        "coeficient": "0.9000",
        "loyer": "297.00",
        "annexes": [],
    }
]
lot1 = {
    "nb_logements": None,
    "financement": "PLUS",
    "type_habitat": "COLLECTIF",
    "logements": logts1,
    "type_stationnements": [],
}
convention1 = {
    "date_fin_conventionnement": None,
    "financement": "PLUS",
    "fond_propre": None,
    "lot": lot1,
    "numero": "0001",
    "statut": "1. Projet",
    "operation_version": programme1,
}
convention1signed = {
    "date_fin_conventionnement": None,
    "financement": "PLUS",
    "fond_propre": None,
    "lot": lot1,
    "numero": "0001",
    "statut": "5. Signée",
    "operation_version": programme1,
}
annexes = [
    {
        "typologie": "COUR",
        "surface_hors_surface_retenue": "5.00",
        "loyer_par_metre_carre": "0.10",
        "loyer": "0.50",
    },
    {
        "typologie": "JARDIN",
        "surface_hors_surface_retenue": "5.00",
        "loyer_par_metre_carre": "0.10",
        "loyer": "0.50",
    },
]
logts2 = [
    {
        "designation": "PLAI 1",
        "typologie": "T1",
        "surface_habitable": "50.00",
        "surface_annexes": "20.00",
        "surface_annexes_retenue": "10.00",
        "surface_utile": "60.00",
        "loyer_par_metre_carre": "5.50",
        "coeficient": "0.9000",
        "loyer": "297.00",
        "annexes": annexes,
    },
    {
        "designation": "PLAI 2",
        "typologie": "T2",
        "surface_habitable": "50.00",
        "surface_annexes": "20.00",
        "surface_annexes_retenue": "10.00",
        "surface_utile": "60.00",
        "loyer_par_metre_carre": "5.50",
        "coeficient": "0.9000",
        "loyer": "297.00",
        "annexes": [],
    },
    {
        "designation": "PLAI 3",
        "typologie": "T3",
        "surface_habitable": "50.00",
        "surface_annexes": "20.00",
        "surface_annexes_retenue": "10.00",
        "surface_utile": "60.00",
        "loyer_par_metre_carre": "5.50",
        "coeficient": "0.9000",
        "loyer": "297.00",
        "annexes": [],
    },
]
lot2 = {
    "nb_logements": None,
    "financement": "PLAI",
    "type_habitat": "MIXTE",
    "logements": logts2,
    "type_stationnements": [],
}
convention2 = {
    "date_fin_conventionnement": None,
    "financement": "PLAI",
    "fond_propre": None,
    "lot": lot2,
    "numero": "0002",
    "statut": "1. Projet",
    "operation_version": programme1,
}
convention2signed = {
    "date_fin_conventionnement": None,
    "financement": "PLAI",
    "fond_propre": None,
    "lot": lot2,
    "numero": "0002",
    "statut": "5. Signée",
    "operation_version": programme1,
}
