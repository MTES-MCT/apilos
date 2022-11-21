bailleur = {
    "nom": "3F",
    "siren": None,
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
}
annexes = [
    {
        "typologie": "CAVE",
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
}
