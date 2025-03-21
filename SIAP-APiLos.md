# Documentation des interactions SIAP APiLos

[Tableau de bord des développements communs entre SIAP et APiLos](https://airtable.com/shruWiCQNMkq6Wggk/tblNIOUJttSKoH866)

## Environnements

| Environnement  | URL SIAP          | URL APiLos version SIAP | Propos de l'environement |
| :--- | :--- |:--- |:--- |
| Production | https://siap.logement.gouv.fr (MTE) | https://apilos.logement.gouv.fr | Partagé avec la version APiLos autonome de production |
| Pilote | https://prehabilitation.siap.logement.gouv.fr (MTE) | ❌ | Préhabilitation et recette de la reprise de donnée, pas d'intérêt d'avoir une plateforme APiLos en mirroir |
| Ecole | https://ecole.siap.logement.gouv.fr (MTE) | https://siap-ecole.apilos.beta.gouv.fr | Utilisé pour les formations |
| Préproduction | https://preprod.siap.logement.gouv.fr (MTE) | ❌ | Peu d'intérêt d'avoir un environnement mirroir APiLos puisse que ce cas est testé sur tous les autres environnements. Proposition : supprimer le lien avec la plateforme APiLos car l'environnement actuellement utilisé est déjà utilisé par la plateforme recette |
| Recette | https://minlog-siap.gateway.recette.sully-group.fr (Sully) | https://siap-recette.apilos.beta.gouv.fr | Rectte métier |
| IntAPI | https://minlog-siap.gateway.intapi.recette.sully-group.fr (Sully) | https://siap-integration.apilos.beta.gouv.fr | Utilisé pour le développement et la validation des fonctionnalités impliquant les 2 plateformes Partagé avec la version APiLos autonome de staging |

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

    Note Over Client: clic sur `Opération > Financement`
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

## Interprétation des Habilitations SIAP

Les habilitations sont interprétées de 3 manières :

1. Les Bailleurs

* Maitre d'ouvrage personne moral
* Maitre d'ouvrage personne physique

Les utilisateurs de type bailleur sont autoirisés à voir et modifier les opérations, conventions et objects associés appartenant à l'entité maitrise d'ouvrage définit par l'habilitation active.

2. Les instructeurs (Service gestionaire)

* Service gestionnaire

Les utilisateurs de type instructeur sont autoirisés à voir et modifier les opérations, conventions et objects associés appartenant à l'entité administrative définit par l'habilitation active.

3. Les administrateurs

* Service départemental
* Direction régionale
* Administration centrale

Les utilisateurs de type administrateur sont autoirisés à voir et modifier les opérations, conventions et objects associés selon la géographie du profile : le département, la région ou la france entièrte définit par l'habilitation active.

## Partage d'objet avec le SIAP

Les objets de la plateforme de financement (SIAP) sont récupérés et créés à la demande sur APiLos dans 2 cas de figure

1. Lorsqu'un utilisateur se connecte sur APiLos:

    1. APiLos vérifie l'authentification de l'utilisateur via CERBERE
    1. APiLos récupère les habilitations de l'utilisateur via le SIAP, l'habilitation active de l'utilisateur est transmise par le SIAP via le paramètre habilitation_id dans l'url. Si ce paramètre n'est pas présent, la première habilitation disponible dans la liste des habilitations récupérées du SIAP sera l'habilitation active.
    1. APilos crée le Bailleur ou l'Administration de l'habilitation active de l'utilisateur si cette entité n'existe pas déjà
    1. Les permissions associées à l'habilitation active sont stockées en session.

2. Lorsqu'un utilisateur accède aux conventions liées à une opération

    1. APiLos récupère les informations liées à l'opération financée
    1. APiLos crée la Bailleur et l'Administration de l'opération si ces entités n'existent pas déjà
    1. APiLos crée l'Opération si cette entité n'existent pas déjà
    1. APiLos crée 1 lots par Aide (PLUS, PLAI, PLS…) si ces lot n'exitent pas déjà, note : l'aide PLAI_ADP (PLAI adapté) sont inclus dans dans l'aide PLAI et nefont pas l'objet de convention spécifique
    1. APiLos crée 1 convention par lots si cette convention n'existe pas déjà

### Détails des objets partagés par le SIAP et repris dans APiLos

On notera : `champ_siap` (`champ_apilos` details)

* Les Administrations
  * champ pivot : `code` (`code` de l'administration)
  * champs repris lors de la création : `libelle` (`nom` de l'administration)

* Les Bailleurs
  * champ pivot : `siren`
  * champs repris lors de la création :
    * `nom` ou `raisonSociale` (`nom` du bailleur)
    * `adresse` interprété des champs d'adresses du SIAP (`adresse`)
    * `codePostal` (`code_postal`)
    * `ville` interprété des champs d'adresses du SIAP (`ville`)
    * `codeFamilleMO` (nature du bailleur)

* Les Opérations (opérations financées via le SIAP)
  * champ pivot : `numeroOperation` (numero_operation)
  * champs repris lors de la création :
    * `nomOperation` (`nom`)
    * `adresse` interprété des champs d'adresses du SIAP (`adresse`)
    * `code_postal` interprété des champs d'adresses du SIAP (`code_postal`)
    * `ville` interprété des champs d'adresses du SIAP (`ville`)
    * `commune`/`codeInsee` (`code_insee_commune`)
    * `departement`/`codeInsee` (`code_insee_departement`)
    * `region`/`codeInsee` (`code_insee_region`)
    * `zonage123` (`zone_abc`)
    * `zonageABC` (`zone_123`)
    * `sansTravaux` ou `sousNatureOperation` (`type_operation`)
    * `natureLogement` (`nature_logement`)

* Les Lots ( un lot par financement et par Opération)
  * champ pivot : `numero` de l'opération + `financement`
  * champs repris lors de la création :
    * `aide`/`code` (`financement`)
    * selon les valeurs `nbLogementsIndividuels`, `nbLogementsCollectifs` (`type_habitat` COLLECTIF, INDIVIDUEL ou MIXTE),
    * `nbLogementsIndividuels` + `nbLogementsCollectifs` (`nb_logements`)

### Les valeurs des listes valuées et leurs correspondances

#### Nature du bailleur (SIAP -> APiLos)

* HLM -> HLM
* SEM -> SEM
* par défaut (toute autre valeur) -> Bailleurs privés

#### Type de l'opération (dépend des champs `sansTravaux` ou `sousNatureOperation`) (SIAP -> APiLos)

* Si `sansTravaux` = 1 -> SANSTRAVAUX
* CNE -> NEUF
* AAM -> ACQUISAMELIORATION
* AST -> ACQUISSANSTRAVAUX
* par défaut (toute autre valeur) -> SANSOBJET

#### Nature logement (SIAP -> APiLos)

* ALF -> AUTRE
* HEB -> HEBERGEMENT
* RES -> RESISDENCESOCIALE
* PEF -> PENSIONSDEFAMILLE
* REA -> RESIDENCEDACCUEIL
* REU -> RESIDENCEUNIVERSITAIRE
* RHVS -> RHVS
* LOO -> LOGEMENTSORDINAIRES

Par défaut la valeur LOGEMENTSORDINAIRES est appliquée

## Pour tester le Client de l'API du SIAP dans un shell (Appel de l'application SIAP à partir du backend de l'application APiLos)

Récupérer l'email de l'utilisteur utilisé pour les tests : généralement votre propre email utilisé pour se connecter à CERBERE
Récupérer l'ID de l'habilitation utilisé pour les tests : les ID sont accéssibles en inspectant les liens du menu permettant de changer d'habilitation en haut à droite de l'écran

Ouvrir un shell django, puis tester quelques appels:

```python
from siap.siap_client.client import SIAPClient
SIAPClient.get_instance().get_habilitations(user_login='user@domain.com')
SIAPClient.get_instance().get_menu(user_login='user@domain.com', habilitation_id=5)
SIAPClient.get_instance().get_operation(user_login='user@domain.com', habilitation_id=27, operation_identifier='20221000003')
SIAPClient.get_instance().get_fusion(user_login='user@domain.com', habilitation_id=123, bailleur_siren="123456789")
```

## Pour tester le Client de l'API d'APiLos dans un shell (Appel de l'application APiLos à partir du backend de l'application SIAP)

Récupérer l'email de l'utilisteur utilisé pour les tests : généralement votre propre email utilisé pour se connecter à CERBERE
Récupérer l'ID de l'habilitation utilisé pour les tests : les ID sont accéssibles en inspectant les liens du menu permettant de changer d'habilitation en haut à droite de l'écran

Ouvrir un shell django, pour générer un Token JWT :

```python
from siap.siap_client.client import build_jwt
build_jwt(user_login="my.name@beta.gouv.fr", habilitation_id=31)
```

Accéder à l'interface de test : <HOST>/api-siap/v0/schema-ui/#/statistics/convention_kpi_list

Cliquez sur le bouton `Authorize` à droite de d'écran et copier le JWT token

L'ensemble des fonctions de la page sont maintenant testables

⚠️ Attention, le token JWT n'est valide que 5 minutes

### Exemple du contenu du token JWT généré par la fonction build_jwt

```json
{
  "iat": 1555458148,
  "exp": 2655458448,
  "token_type": "access",
  "jti": "c14f318c99024a398a39281d3827e612",
  "user-login": "user@domain.com",
  "habilitation-id": 6
}
```

Il est possible aussi de générer de token via un site tel que https://jwt.io/ et en utilisant la clé JWT_SIGN_KEY pour signer le token

## Questions ouvertes pour plus tard :

- [ ] Comment retrouver les paramètres propres à APiLos dans la version SIAP
- [ ] Deloguer sur le SIAP / Apilos doit délogguer des 2 plateformes
