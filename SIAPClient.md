# Documentation des interactions SIAP APiLos

## Cas d'utilisation

### Autentification au SIAP ou APiLos via CERBERE

L'authentification via CERBERE utilise le même protocole pour SIAP et APiLos

```mermaid

sequenceDiagram
    actor Client
    participant SIAP / APiLos
    participant CERBERE

    Note over Client, CERBERE : Client non authentifié
    Client->>+SIAP / APiLos: Accès à l'application
    Client->>CERBERE: Redirection pour authentification
    Note over CERBERE: Authentification
    CERBERE->>Client: Redirection avec token
    Client->>SIAP / APiLos: Accès avec token
    SIAP / APiLos->>CERBERE: Vérification du token
    SIAP / APiLos->>-Client: Accès identifié
    Note over Client, CERBERE : Client authentifié

```

Bloc nommé `Authentification via CERBERE` dans la suite du document

### Connexion au SIAP et redirection APiLos / SIAP via le menu

```mermaid

sequenceDiagram
    actor Client
    participant SIAP
    participant APiLos

    Client->>+SIAP: Accès à la plateforme
    Note over Client, APiLos: Authentification via CERBERE
    SIAP->>-Client: Affichage de la plateforme
    Note Over Client: clic sur `Oprération > Conventionnement`

    Client->>+APiLos: Redirection vers APiLos<br>avec habilitation_id active dans l'url
    Note over Client, APiLos: Authentification via CERBERE
    APiLos->>SIAP: GET habilitations
    APiLos->>APiLos: CREATE IF NOT EXIST de l'entité de l'habilitation
    APiLos->>SIAP: GET menu
    APiLos->>-Client: Affichage de l'application avec l'entête selon habilitations

    Note Over Client: clic sur `Oprération > Financement`
    Client->>SIAP: Redirection vers APiLos<br>avec habilitation_id active dans l'url

```


### Bascule vers le conventionnement à partir d'une opération SIAP

```mermaid

sequenceDiagram
    actor Client
    participant SIAP
    participant APiLos

    Client->>+SIAP: Affichage d'une opération
    Note over Client, APiLos: Authentification via CERBERE
    SIAP->>-Client: Affichage d'une opération
    Note Over Client: clic sur `Conventionner l'opération`
    Client->>+APiLos: Accès à l'application
    Note over Client, APiLos: Authentification via CERBERE
    APiLos->>SIAP: GET habilitations
    APiLos->>APiLos: CREATE IF NOT EXIST de l'entité de l'habilitation
    APiLos->>SIAP: GET menu
    APiLos->>SIAP: GET operation
    APiLos->>APiLos: CREATE IF NOT EXIST des conventions de l'opération
    APiLos->>-Client: Affichage des conventions de l'opération

```


### Affichage des indicateurs de conventionnement dans le ableau de bord du SIAP

```mermaid

sequenceDiagram
    actor Client
    participant SIAP
    participant APiLos

    Client->>+SIAP: Accès au taleau de bord
    Note over Client, APiLos: Authentification via CERBERE

    SIAP->>+APiLos: GET indicateur de conventionnement <br> avec utilisateur et habilitation_id
    APiLos->>SIAP: GET habilitations
    APiLos->>APiLos: CREATE IF NOT EXIST de l'entité de l'habilitation
    APiLos->>-SIAP: retour des indicateurs de conventionnement
    SIAP->>-Client: Affichage du tableau de bord

```


## Pour tester SIAP Client dans un shell :

Ouvrir un shell django

Puis test de quelques appels:

```python
>>> from siap.siap_client.client import SIAPClient
>>> SIAPClient.get_instance().get_habilitations(user_login='nicolas.oudard@beta.gouv.fr')
>>> SIAPClient.get_instance().get_menu(user_login='nicolas.oudard@beta.gouv.fr', habilitation_id=5)
>>> SIAPClient.get_instance().get_operation(user_login='nicolas.oudard@beta.gouv.fr', habilitation_id=5, operation_identifier='20220600005')
```

## Todo

- [x] Affichage des habilitations dans l’en-tête
- [x] Affichage du menu dans l’entête
- [x] Création des environnements integration recette preprod
- [x] Résoudre les pb d’appel aux API menu et opération
- [x] Création d’une route API permettant au SIAP de récupérer le détail des conventions
- [x] Création d’une route API permettant d’afficher les indicateurs
- [x] Intégration du design de l’entête
- [x] Mapping SIAP / APiLos en utilisant les routes SIAP>opération et APiLos>opération
- [x] Création de l’entité de l'utilisateur (Administration ou Bailleur) si elle n’existe pas
- [x] Retourner les indicateurs selon l'habilitation active de l'utilisateur
- [x] Affichage de la liste des conventions selon l’habilitation
- [x] Création des conventions et affichage des conventions à faire pour un opération données
- [x] Ajout d'un lien vers l'opération du SIAP à partir de la convention
- [x] Adaptation de l'interface pour le SIAP
- [ ] **Démarrage de l'expérimentation**
- [x] Recharger régulièrement la configuration du client SIAP
- [x] Controle de la signature JWT sur la route config
- [ ] BUG : Opération créée de zero -> erreur avant l'appel à l'API SIAP
- [ ] Route operation_modifiee notifie APiLos de la modification d'une opération (utilisé pour les opérations engagées et plus si besoin selon les évolutions métiers)
- [x] Ajouter logements, annexes et stationnements à l'API /opération de APiLos
- [ ] Gestion des conventions sans travaux à partir du SIAP
- [ ] Mis à jour du client suivant les évolutions de l'API SIAP (habilitation valide, bailleur...)
    - [ ] Affichage des habilitations selon un paramètre `"valide": True,`
    - [ ] siret / siren

```
            "entiteMorale": {
                "nom": "3F GRAND EST",
                "siren": "498273556",
                "siret": "49827355600123", ???
```

    - [ ] adresse sur 2 lignes

```
        "adresse": " Allée de l’Aubepine 13010 Marseille",
VERS
        "adresseLigne4": "80 RUE ALBE",
        "adresseLigne6": "13004 MARSEILLE 4",
```

- [ ] Application des autres type d'habilitation (autre que Bailleur et Instructeur)
    - [ ] Affichage des conventions en lecture seule
    - [ ] Affichage des conventions selon la géographie
- [ ] Envoi de mail à partir d'une convention SIAP
- [ ] Affichage des statistiques du conventionnement
- [ ] Miror du repo github dans [gitlab](https://gitlab-forge.din.developpement-durable.gouv.fr/dgaln/dhup/apilos) pour le SNUM
- [ ] Mis à jour des Roles de l'utilisateur pour supprimer les roles obsolètes (à faire lors de la récup des habilitations ?)


Questions ouvertes pour plus tard :

- [ ] Comment retrouver les paramètres propres à APiLos dans la version SIAP
- [ ] Deloguer sur le SIAP / Apilos doit délogguer des 2 plateformes


## token exemple

```json
{
  "iat": 1655458148,
  "exp": 1655458448,
  "jti": "9f192912-426b-41c2-a8a5-ab51077a27fd",
  "user-login": "nicolas.oudard@beta.gouv.fr",
  "habilitation-id": 5
}
```
