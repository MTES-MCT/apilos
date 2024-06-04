config_mock = {
    "racineUrlAccesWeb": "https://minlog-siap.gateway.intapi.recette.sully-group.fr",
    "urlAccesWeb": "/tableau-bord",
    "urlAccesWebOperation": (
        "/operation/mes-operations/editer/<NUM_OPE_SIAP>/informations-generales"
    ),
}

habilitations_mock = {
    "habilitations": [
        {
            "id": 5,
            "groupe": {
                "id": 28,
                "profil": {
                    "code": "MO_PERS_MORALE",
                    "libelle": "Maître d’ouvrage personne morale",
                },
                "codeRole": "MO_MORAL_REG_ADMIN",
                "libelleRole": "Administrateur délégué",
                "codePorteeTerrit": "REG",
                "isSignataire": False,
                "typeDelegation": None,
            },
            "gestionnaire": {
                "id": None,
                "code": None,
                "libelle": None,
                "typeDelegation": None,
                "typeDelegataire": None,
                "typeLocalisation": None,
            },
            "entiteMorale": {
                "nom": "13 HABITAT",
                "siren": "782855696",
                "commune": {
                    "id": 4527,
                    "libelle": "Marseille - 4e arrondissement (13)",
                },
                "adresseLigne3": None,
                "adresseLigne4": "80 RUE ALBE",
                "adresseLigne6": "13004 MARSEILLE 4",
            },
            "dateExpiration": "2028-06-10",
            "dateDemande": "2022-06-10",
            "favori": False,
            "porteeTerritComp": {
                "id": 8,
                "codePortee": "REG",
                "regComp": {
                    "id": 15,
                    "libelle": "Provence-Alpes-Côte d'Azur",
                    "code": 93,
                },
                "depComp": None,
                "epciComp": None,
                "comComp": None,
                "libellee": "Provence-Alpes-Côte d'Azur",
                "territoireIntervention": "Provence-Alpes-Côte d'Azur",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "my.name@beta.gouv.fr",
            },
            "sousTitre1": "SIREN 782855696",
            "sousTitre2": "Provence-Alpes-Côte d'Azur",
        },
        {
            "id": 3,
            "groupe": {
                "id": 1,
                "profil": {
                    "code": "ADM_CENTRALE",
                    "libelle": "Administration centrale",
                },
                "codeRole": "ADM_CENTRALE_ADMIN",
                "libelleRole": "Administrateur national",
                "codePorteeTerrit": "NAT",
                "isSignataire": False,
                "typeDelegation": None,
            },
            "gestionnaire": {
                "id": None,
                "code": None,
                "libelle": None,
                "typeDelegation": None,
                "typeDelegataire": None,
                "typeLocalisation": None,
            },
            "entiteMorale": None,
            "dateExpiration": "2028-06-10",
            "dateDemande": "2022-06-10",
            "favori": False,
            "porteeTerritComp": {
                "id": 4,
                "codePortee": "NAT",
                "regComp": None,
                "depComp": None,
                "epciComp": None,
                "comComp": None,
                "libellee": "France entière",
                "territoireIntervention": "France entière",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "my.name@beta.gouv.fr",
            },
            "sousTitre1": None,
            "sousTitre2": "France entière",
        },
        {
            "id": 12,
            "groupe": {
                "id": 20,
                "profil": {"code": "SER_GEST", "libelle": "Service gestionnaire"},
                "codeRole": "SERV_INSTR_DELGEG3_INSTRUCTEUR",
                "libelleRole": "Instructeur",
                "codePorteeTerrit": "LOC",
                "isSignataire": False,
                "typeDelegation": "T3",
            },
            "gestionnaire": {
                "id": 9,
                "code": "13055",
                "libelle": "13055 - Métropole d'Aix-Marseille-Provence",
                "typeDelegation": "3",
                "typeDelegataire": "1",
                "typeLocalisation": None,
            },
            "entiteMorale": None,
            "dateExpiration": "2028-06-20",
            "dateDemande": "2022-06-20",
            "favori": False,
            "porteeTerritComp": {
                "id": 26,
                "codePortee": "EPCI",
                "regComp": {
                    "id": 15,
                    "libelle": "Provence-Alpes-Côte d'Azur",
                    "code": 93,
                },
                "depComp": {"id": 13, "libelle": "Bouches du Rhône", "code": 13},
                "epciComp": {
                    "id": 276,
                    "libelle": "Métropole d'Aix-Marseille-Provence",
                },
                "comComp": None,
                "libellee": "Métropole d'Aix-Marseille-Provence",
                "territoireIntervention": "Métropole d'Aix-Marseille-Provence",
            },
            "territComp": None,
            "statut": "VALIDEE",
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "my.name@beta.gouv.fr",
            },
            "sousTitre1": "13055 - Métropole d'Aix-Marseille-Provence",
            "sousTitre2": None,
        },
        {
            "id": 38,
            "groupe": {
                "id": 3,
                "profil": {"code": "DIR_REG", "libelle": "Direction régionale"},
                "codeRole": "DIR_REG_ADMIN",
                "libelleRole": "Administrateur régional",
                "codePorteeTerrit": "REG",
                "isSignataire": False,
                "typeDelegation": None,
            },
            "gestionnaire": {
                "id": 274,
                "code": "DR013",
                "libelle": "Provence-Alpes-Côte d'Azur",
                "typeDelegation": None,
                "typeDelegataire": "3",
                "typeLocalisation": None,
            },
            "entiteMorale": None,
            "dateExpiration": "2028-06-23",
            "dateDemande": "2022-06-23",
            "favori": False,
            "porteeTerritComp": {
                "id": 96,
                "codePortee": "REG",
                "regComp": {
                    "id": 15,
                    "libelle": "Provence-Alpes-Côte d'Azur",
                    "code": 93,
                },
                "depComp": None,
                "epciComp": None,
                "comComp": None,
                "libellee": "Provence-Alpes-Côte d'Azur",
                "territoireIntervention": "Provence-Alpes-Côte d'Azur",
            },
            "territComp": None,
            "statut": "A_VALIDER",
            "titre": None,
            "adresse": None,
            "utilisateur": {
                "nom": "OUDARD",
                "prenom": "Nicolas",
                "email": "my.name@beta.gouv.fr",
            },
            "sousTitre1": "Provence-Alpes-Côte d'Azur",
            "sousTitre2": None,
        },
    ]
}

menu_mock = {
    "menuItems": [
        {
            "libelle": "Tableau de bord",
            "active": True,
            "url": "/tableau-bord",
            "menuItems": [],
        },
        {
            "libelle": "Habilitation",
            "active": True,
            "url": "/admin-habilitation",
            "menuItems": [
                {
                    "libelle": "Gestion des demandes",
                    "active": True,
                    "url": "/admin-habilitation/gestion-demandes-habilitation",
                    "menuItems": [],
                },
                {
                    "libelle": "Gestion des utilisateurs",
                    "active": True,
                    "url": "/admin-habilitation/gestion-utilisateurs",
                    "menuItems": [],
                },
            ],
        },
        {
            "libelle": "Mes opérations",
            "active": True,
            "url": "/operation",
            "menuItems": [
                {
                    "libelle": "Financement",
                    "active": True,
                    "url": "/operation/mes-operations",
                    "menuItems": [],
                },
                {
                    "libelle": "Conventionnement",
                    "active": True,
                    "url": "https://preprod.apilos.beta.gouv.fr/conventions",
                    "menuItems": [],
                },
            ],
        },
    ]
}

operation_mock = {
    "donneesMo": {
        "nom": "3F",
        "siren": "782855696",
        "commune": None,
        "adresseLigne3": "",
        "adresseLigne4": "80 rue d'Albe BP 31",
        "adresseLigne6": "13234 Marseille - 4e arrondissement",
        "codeFamilleMO": "HLM",
    },
    "donneesLocalisation": {
        "region": {"codeInsee": "93", "libelle": None},
        "departement": {"codeInsee": "13", "libelle": None},
        "commune": {"codeInsee": "13210", "libelle": "Marseille - 10e arrondissement"},
        "adresse": "Rue Francois Mauriac 13010 Marseille",
        "adresseComplete": {
            "adresse": "Rue Francois Mauriac ",
            "codePostal": "13010",
            "commune": "Marseille",
            "codePostalCommune": "13010 Marseille",
        },
        "zonage123": "02",
        "zonageABC": "A",
    },
    "donneesOperation": {
        "nomOperation": "Programme 2",
        "numeroOperation": "20220600006",
        "aides": [{"code": "PLUS", "libelle": "PLUS"}],
        "sousNatureOperation": "CNE",
        "typeConstruction": "TC_C",
        "natureLogement": "LOO",
        "sansTravaux": False,
    },
    "detailsOperation": [
        {
            "aide": {"code": "PLUS", "libelle": "PLUS"},
            "logement": {"nbLogementsIndividuels": None, "nbLogementsCollectifs": 1},
            "detailsTypeLogement": [
                {
                    "typeLogement": "T1",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1BIS",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1P",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T2",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T3",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T4",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T5",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T6",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
            ],
            "garages": [
                {
                    "type": "Enterrés / Sous-sol",
                    "nbGaragesIndividuels": None,
                    "nbGaragesCollectifs": 0,
                },
                {
                    "type": "Superstructure",
                    "nbGaragesIndividuels": None,
                    "nbGaragesCollectifs": 0,
                },
            ],
            "loyers": [
                {
                    "type": "Collectif",
                    "loyerZone": 5.78,
                    "loyerBase": 0.0,
                    "loyerReglementaire": 0.0,
                    "loyerPratique": 0,
                    "loyerGarages": [
                        {"type": "Enterrés / Sous-sol", "loyer": 0},
                        {"type": "Superstructure", "loyer": 0},
                    ],
                }
            ],
        }
    ],
    "planFinancement": {
        "subventions": [{"type": "PLUS", "montant": None}],
        "prets": [],
        "fondsPropres": 0,
    },
    "gestionnaire": {
        "id": 9,
        "code": "13055",
        "libelle": "13055 - Métropole d'Aix-Marseille-Provence",
        "typeDelegation": "3",
        "typeDelegataire": "1",
        "typeLocalisation": "EPCI3",
        "adresse": None,
        "commune": None,
        "email": None,
        "utilisateurs": [
            {
                "login": "my.name@beta.gouv.fr",
                "email": "my.name@beta.gouv.fr",
                "groupes": [
                    {
                        "id": 20,
                        "profil": {
                            "code": "SER_GEST",
                            "libelle": "Service gestionnaire",
                        },
                        "codeRole": "SERV_INSTR_DELGEG3_INSTRUCTEUR",
                        "libelleRole": "Instructeur",
                        "codePorteeTerrit": "LOC",
                        "typeDelegation": "T3",
                    }
                ],
            }
        ],
    },
}
operation_mock2 = {
    "donneesMo": {
        "nom": "13 HABITAT",
        "siren": "782855696",
        "commune": None,
        "adresseLigne3": "",
        "adresseLigne4": "80 rue d'Albe BP 31",
        "adresseLigne6": "13234 Marseille - 4e arrondissement",
        "codeFamilleMO": "HLM",
    },
    "donneesLocalisation": {
        "region": {"codeInsee": "93", "libelle": None},
        "departement": {"codeInsee": "13", "libelle": None},
        "commune": {"codeInsee": "13210", "libelle": "Marseille - 10e arrondissement"},
        "adresse": "10 Rue de salon 13010 Marseille",
        "adresseComplete": {
            "adresse": "10 Rue de salon",
            "codePostal": "13010",
            "codeInseeCommune": None,
            "commune": "Marseille",
            "codePostalCommune": "13010 Marseille",
        },
        "zonage123": "02",
        "zonageABC": "A",
    },
    "donneesOperation": {
        "nomOperation": "APiLos",
        "numeroOperation": "20221200002",
        "aides": [
            {"code": "PLUS", "libelle": "PLUS"},
            {"code": "PLAI", "libelle": "PLAI"},
        ],
        "sousNatureOperation": "CNE",
        "typeConstruction": "TC_I",
        "natureLogement": "LOO",
        "sansTravaux": False,
    },
    "detailsOperation": [
        {
            "aide": {"code": "PLUS", "libelle": "PLUS"},
            "logement": {"nbLogementsIndividuels": 10, "nbLogementsCollectifs": None},
            "detailsTypeLogement": [
                {
                    "typeLogement": "T1",
                    "nbLogements": 10,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1BIS",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1P",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T2",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T3",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T4",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T5",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T6",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
            ],
            "garages": [
                {
                    "type": "Enterrés / Sous-sol",
                    "nbGaragesIndividuels": 0,
                    "nbGaragesCollectifs": None,
                },
                {
                    "type": "Superstructure",
                    "nbGaragesIndividuels": 0,
                    "nbGaragesCollectifs": None,
                },
            ],
            "loyers": [
                {
                    "type": "Individuel",
                    "loyerZone": 0.0,
                    "loyerBase": 0.0,
                    "loyerReglementaire": 0.0,
                    "loyerPratique": 0,
                    "loyerGarages": [
                        {"type": "Enterrés / Sous-sol", "loyer": 0},
                        {"type": "Superstructure", "loyer": 0},
                    ],
                }
            ],
        },
        {
            "aide": {"code": "PLAI", "libelle": "PLAI"},
            "logement": {"nbLogementsIndividuels": 10, "nbLogementsCollectifs": None},
            "detailsTypeLogement": [
                {
                    "typeLogement": "T1",
                    "nbLogements": 10,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1BIS",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1P",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T2",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T3",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T4",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T5",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T6",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
            ],
            "garages": [
                {
                    "type": "Enterrés / Sous-sol",
                    "nbGaragesIndividuels": 0,
                    "nbGaragesCollectifs": None,
                },
                {
                    "type": "Superstructure",
                    "nbGaragesIndividuels": 0,
                    "nbGaragesCollectifs": None,
                },
            ],
            "loyers": [
                {
                    "type": "Individuel",
                    "loyerZone": 0.0,
                    "loyerBase": 0.0,
                    "loyerReglementaire": 0.0,
                    "loyerPratique": 0,
                    "loyerGarages": [
                        {"type": "Enterrés / Sous-sol", "loyer": 0},
                        {"type": "Superstructure", "loyer": 0},
                    ],
                }
            ],
        },
    ],
    "plansFinancement": [
        {
            "repartitionAideComp": None,
            "subventions": [
                {"type": "PLAI", "montant": 100},
                {"type": "PLUS", "montant": 100},
            ],
            "prets": [],
            "aidesFisclaes": None,
            "fondsPropres": 0,
            "codeAide": "PLUS",
        },
        {
            "repartitionAideComp": None,
            "subventions": [
                {"type": "PLAI", "montant": 100},
                {"type": "PLUS", "montant": 100},
            ],
            "prets": [],
            "aidesFisclaes": None,
            "fondsPropres": 3000,
            "codeAide": "PLAI",
        },
    ],
    "gestionnaire": {
        "id": 9,
        "code": "13055",
        "libelle": "13055 - Métropole d'Aix-Marseille-Provence",
        "typeDelegation": "3",
        "typeDelegataire": "1",
        "typeLocalisation": "EPCI3",
        "adresse": None,
        "commune": None,
        "email": None,
        "utilisateurs": [
            {
                "login": "my.name@beta.gouv.fr",
                "email": "my.name@beta.gouv.fr",
                "groupes": [
                    {
                        "id": 19,
                        "profil": {
                            "code": "SER_GEST",
                            "libelle": "Service gestionnaire",
                        },
                        "codeRole": "SERV_INSTR_DELGEG3_ADMIN",
                        "libelleRole": "Administrateur",
                        "codePorteeTerrit": "LOC",
                        "typeDelegation": "T3",
                    },
                    {
                        "id": 20,
                        "profil": {
                            "code": "SER_GEST",
                            "libelle": "Service gestionnaire",
                        },
                        "codeRole": "SERV_INSTR_DELGEG3_INSTRUCTEUR",
                        "libelleRole": "Instructeur",
                        "codePorteeTerrit": "LOC",
                        "typeDelegation": "T3",
                    },
                    {
                        "id": 22,
                        "profil": {
                            "code": "SER_GEST",
                            "libelle": "Service gestionnaire",
                        },
                        "codeRole": "SERV_INSTR_DELGEG3_SIGNATAIRE",
                        "libelleRole": "Signataire",
                        "codePorteeTerrit": "LOC",
                        "typeDelegation": "T3",
                    },
                    {
                        "id": 21,
                        "profil": {
                            "code": "SER_GEST",
                            "libelle": "Service gestionnaire",
                        },
                        "codeRole": "SERV_INSTR_DELGEG3_VALIDEUR",
                        "libelleRole": "Valideur",
                        "codePorteeTerrit": "LOC",
                        "typeDelegation": "T3",
                    },
                ],
            }
        ],
    },
    "gestionnaireSecondaire": {
        "id": 9,
        "code": "13055",
        "libelle": "13055 - Métropole d'Aix-Marseille-Provence",
        "typeDelegation": "3",
        "typeDelegataire": "1",
        "typeLocalisation": "EPCI3",
        "adresse": None,
        "commune": None,
        "email": None,
        "utilisateurs": [
            {
                "login": "my.name@beta.gouv.fr",
                "email": "my.name@beta.gouv.fr",
                "groupes": [
                    {
                        "id": 19,
                        "profil": {
                            "code": "SER_GEST",
                            "libelle": "Service gestionnaire",
                        },
                        "codeRole": "SERV_INSTR_DELGEG3_ADMIN",
                        "libelleRole": "Administrateur",
                        "codePorteeTerrit": "LOC",
                        "typeDelegation": "T3",
                    },
                    {
                        "id": 20,
                        "profil": {
                            "code": "SER_GEST",
                            "libelle": "Service gestionnaire",
                        },
                        "codeRole": "SERV_INSTR_DELGEG3_INSTRUCTEUR",
                        "libelleRole": "Instructeur",
                        "codePorteeTerrit": "LOC",
                        "typeDelegation": "T3",
                    },
                    {
                        "id": 22,
                        "profil": {
                            "code": "SER_GEST",
                            "libelle": "Service gestionnaire",
                        },
                        "codeRole": "SERV_INSTR_DELGEG3_SIGNATAIRE",
                        "libelleRole": "Signataire",
                        "codePorteeTerrit": "LOC",
                        "typeDelegation": "T3",
                    },
                    {
                        "id": 21,
                        "profil": {
                            "code": "SER_GEST",
                            "libelle": "Service gestionnaire",
                        },
                        "codeRole": "SERV_INSTR_DELGEG3_VALIDEUR",
                        "libelleRole": "Valideur",
                        "codePorteeTerrit": "LOC",
                        "typeDelegation": "T3",
                    },
                ],
            }
        ],
    },
}

fusion_mock = [
    {
        "sirenAbsorbe": "271200024",
        "sirenAbsorbant": "426580114",
        "dateFinValidite": "2023-09-29",
    }
]

operation_seconde_vie_mock = {
    "donneesMo": {
        "nom": "3F",
        "siren": "782855696",
        "commune": None,
        "adresseLigne3": "",
        "adresseLigne4": "80 rue d'Albe BP 31",
        "adresseLigne6": "13234 Marseille - 4e arrondissement",
        "codeFamilleMO": "HLM",
    },
    "donneesLocalisation": {
        "region": {"codeInsee": "93", "libelle": None},
        "departement": {"codeInsee": "13", "libelle": None},
        "commune": {"codeInsee": "13210", "libelle": "Marseille - 10e arrondissement"},
        "adresse": "Rue Francois Mauriac 13010 Marseille",
        "adresseComplete": {
            "adresse": "Rue Francois Mauriac ",
            "codePostal": "13010",
            "commune": "Marseille",
            "codePostalCommune": "13010 Marseille",
        },
        "zonage123": "02",
        "zonageABC": "A",
    },
    "donneesOperation": {
        "nomOperation": "Programme 2",
        "numeroOperation": "20220600016",
        "aides": [{"code": "SECD_VIE", "libelle": "Seconde vie"}],
        "sousNatureOperation": "CNE",
        "typeConstruction": "TC_C",
        "natureLogement": "LOO",
        "sansTravaux": False,
    },
    "detailsOperation": [
        {
            "aide": {"code": "PLUS", "libelle": "PLUS"},
            "logement": {"nbLogementsIndividuels": None, "nbLogementsCollectifs": 1},
            "detailsTypeLogement": [
                {
                    "typeLogement": "T1",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1BIS",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T1P",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T2",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T3",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T4",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T5",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
                {
                    "typeLogement": "T6",
                    "nbLogements": None,
                    "surfaceHabitable": None,
                    "surfaceAnnexe": None,
                },
            ],
            "garages": [
                {
                    "type": "Enterrés / Sous-sol",
                    "nbGaragesIndividuels": None,
                    "nbGaragesCollectifs": 0,
                },
                {
                    "type": "Superstructure",
                    "nbGaragesIndividuels": None,
                    "nbGaragesCollectifs": 0,
                },
            ],
            "loyers": [
                {
                    "type": "Collectif",
                    "loyerZone": 5.78,
                    "loyerBase": 0.0,
                    "loyerReglementaire": 0.0,
                    "loyerPratique": 0,
                    "loyerGarages": [
                        {"type": "Enterrés / Sous-sol", "loyer": 0},
                        {"type": "Superstructure", "loyer": 0},
                    ],
                }
            ],
        }
    ],
    "planFinancement": {
        "subventions": [{"type": "PLUS", "montant": None}],
        "prets": [],
        "fondsPropres": 0,
    },
    "gestionnaire": {
        "id": 9,
        "code": "13055",
        "libelle": "13055 - Métropole d'Aix-Marseille-Provence",
        "typeDelegation": "3",
        "typeDelegataire": "1",
        "typeLocalisation": "EPCI3",
        "adresse": None,
        "commune": None,
        "email": None,
        "utilisateurs": [
            {
                "login": "my.name@beta.gouv.fr",
                "email": "my.name@beta.gouv.fr",
                "groupes": [
                    {
                        "id": 20,
                        "profil": {
                            "code": "SER_GEST",
                            "libelle": "Service gestionnaire",
                        },
                        "codeRole": "SERV_INSTR_DELGEG3_INSTRUCTEUR",
                        "libelleRole": "Instructeur",
                        "codePorteeTerrit": "LOC",
                        "typeDelegation": "T3",
                    }
                ],
            }
        ],
    },
}
