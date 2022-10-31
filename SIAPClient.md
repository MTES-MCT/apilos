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
>>> SIAPClient.get_instance().get_operation(user_login='nicolas.oudard@beta.gouv.fr', habilitation_id=27, operation_identifier='20221000003')
```

## Questions ouvertes pour plus tard :

- [ ] Comment retrouver les paramètres propres à APiLos dans la version SIAP
- [ ] Deloguer sur le SIAP / Apilos doit délogguer des 2 plateformes

## token exemple

```json
{
  "iat": 2655458148,
  "exp": 2655458448,
  "token_type": "access",
  "jti": "9f192912-426b-41c2-a8a5-ab51077a27fd",
  "user-login": "nicolas.oudard@beta.gouv.fr",
  "habilitation-id": 339
}
```
