```{toctree}
```

# DEVELOPPEMENT

Cette documentation décrit toutes les étapes nécessaires à l'intallation et au développement de la plateforme APiLos.

Les règles et standards de codage y sont décrits

## Quelques détails sur la stack technique utilisée

### Framework et langages de programmation

#### Django / Python

On utilise le framework python Django

Dans la plus part des cas la logique logicielle est découpée comme suit

* Les vues : prennent en charges les permissions et affichages des pages
* Les services : prennent en charge la logique métier avec l'execution des formulaires
* Les formulaires : définissent les règles métiers
* Les models : assurent la cohérence du schéma et des objets en base de données

##### Génération de documents xls et pdf

APiLos est un outils permettant de générer un document contractuel de convention APL.

La génération de document de convention au format .docx est prise en charge par la librairie [python-docx-template](https://docxtpl.readthedocs.io/en/latest/) qui utilise le moteur de template Jinja2 pour modifier le template des documents de conventions APL. Les templates de docuements sont dans le dossier [./documents](https://github.com/MTES-MCT/apilos/tree/main/documents)

Une fois la convention validée par les deux parties, celle-ci est envoyée au format pdf par email au bailleur.
L'application [Libreoffice](https://https://fr.libreoffice.org/discover/libreoffice/) est utilisée pour générer une version pdf du document docx.

##### Import de firchiers excel

Lors de l'instruction des conventions, les bailleurs téléversent des tableaux de cadastres, financements, logements, annexes.
Le package openpyxl est utilisé pour l'interprétation des fichiers xlsx

## Installation

La plateforme APiLos est open source et la gestion de version est assuré via Github. La première étape est donc de cloner ce repository github.

### Prérequis

Les services Postgresql et Redis utilisés par APiLos sont dockerisés
Python et Node sont nécessaires pour lancer l'application
Il est conseillé d'installer un environnment virtuel pour isoler l'environnement python et node d'APiLos (asdf par exemple)

* Python >=3.12
* Node >=18.14
* docker
* docker-compose
* Client Scalingo nécessaire pour faire tourner certaine commande

### Client Scalingo

Installer et configurer le client Scalingo : https://doc.scalingo.com/platform/cli/start

### Javascript

Peu de JS est utilisé dans l'application.
Les dépendances sont déclarées dans le fichier [package.json](https://github.com/MTES-MCT/apilos/tree/main/package.json)

Avant de lancer l'application, il est nécessaire d'installer ces dépendances:

```sh
npm install
```

### Environment virtuel python

Générer votre environnement virtuel

```sh
python -m venv .venv --prompt $(basename $(pwd))
source .venv/bin/activate
```

### Services docker

Les services `Postgresql` et `Redis` sont lancés avec Docker Compose

```sh
docker-compose build
docker-compose up -d
```

### Variables d'environnement

Copier les [.env.template](https://github.com/MTES-MCT/apilos/tree/main/.env.template) dans un fichier `.env` et [.env.test](https://github.com/MTES-MCT/apilos/tree/main/.env.test) dans `.env.test.local`.

```sh
cp .env.template .env
cp .env.test .env.test.local
```

Puis mettre à jour les variables d'environements si nécessaire, par exemple:

```ini
DB_USER=apilos
DB_NAME=apilos
DB_HOST=localhost
DB_PASSWORD=apilos
DB_PORT=5433
```

### Installer les dépendances python

On utilise pip-tools pour gérer les dépendances `python`

```sh
pip install pip-tools
pip install -r requirements.txt -r dev-requirements.txt
```

### Modifier ses DNS locaux

Ajouter la ligne au ficher `/etc/hosts`

```
127.0.0.1	local.beta.gouv.fr
```

⚠️ Pour les utilisateurs de Windows + WSL, la modification du `etc/hosts` doit aussi être faite sur Windows.

## Lancement de l'application

On utilise la librairie  `honcho` en environnement de développement pour lancer les services django server et celery workers dont les commandes sont définis dans le fichier [Procfile.dev](https://github.com/MTES-MCT/apilos/tree/main/Procfile.dev)

```sh
honcho start -f Procfile.dev
```

L'application est désormais disponible à l'adresse [http://localhost:8001](http://localhost:8001)

### Population de la base de donnnées en environnement de développement

Le plus simple est de récupérer un backup de la base de données de l'environnement d'integration via l'interface de Scalingo et de le restaurer localement

```sh
make db-restore
```

### ClamAV (optionnel)

ClamAV est utilisé pour le scan des fichiers uploadés.
Une version _as-a-service_ est utilisée.
Pour développer localement, il est nécessaire d'utiliser [le projet dédié](https://github.com/betagouv/clamav-service).

Pour l'utiliser, depuis un autre répertoire que le dépôt courant :

```sh
git clone git@github.com:betagouv/clamav-service.git
cd clamav-service
make up
```

Le service expose l'API sur le port 3310, celui-ci doit être défini dans le fichier `.env` de `APiLos`.
Basé sur `.env.template`, définir la variable d'environnement `CLAMAV_SERVICE_URL` dans le fichier `.env` :

```sh
# .env
# other environment variables ...
CLAMAV_SERVICE_URL=http://localhost:3310
```

### Gestion des accès via CERBERE / SIAP

Créer des accès en Integration (accès qui servent aussi pour l'environement local) et en production

#### Denamde d'accès CERBERE

Faire une demande via le lien `Créer un compte` des pages CERBERE :

- Integration : [CERBERE RECETTE > point d'accès SIAP](https://authentification.recette.din.developpement-durable.gouv.fr/cas/576/login?service=https%3A%2F%2Fsiap-integration.apilos.beta.gouv.fr%2Faccounts%2Fcerbere-login%3Fnext%3D%252F)
- Production : [CERBERE PROD > point d'accès SIAP](https://authentification.din.developpement-durable.gouv.fr/cas/700/login?service=https%3A%2F%2Fapilos.logement.gouv.fr%2Faccounts%2Fcerbere-login%3Fnext%3D%252F)

Utiliser la demande par numéro de SIREN (initialement le numéro de SIREN de la DINUM était utilisé).

Sur l'environnement CERBERE de Recette, il est nécessaire de faire valider son compte : voir avec le chef de projet du SIAP.

#### Demande d'abilitation SIAP

Après la création des accès CERBERE, il est nécessaire de demander des habilitations:

- en Integration : Administration central /Administrateur nationnal
- en Production : Administration central / Lecture seule

Ces habilitations doivent être valider par un personne qui a les droits : voir avec le chef de projet du SIAP.

### Accès à APiLos

A partir du SIAP sur tous les evironnement, APiLos ets disponible dans le menu : `Mes Opération` > `Conventionnement`

Ou en accédant directement à l'URL:

* En local : http://local.beta.gouv.fr:8001/
* En integration : https://siap-integration.apilos.beta.gouv.fr/
* En Production : https://apilos.logement.gouv.fr/

## Qualité de code

### Tests

La librairie pytest est utilisée pour lancer les tests.
Quelques tests d'intégration utilisent la libraire `beautifulsoup` quand il est nécessaire d'inspecter le DOM.
La librairie factory_boy est utilisé pour gérer des fixtures

Les tests sont organisés comme suit :

* Tests unitaires : APPNAME/tests/models/…
* Tests integration : APPNAME/tests/views/… APPNAME/tests/services/…

#### Lancement des tests

L'application prend en charge des test unitaire et des tests d'intégration. Pour les lancer:

```sh
pytest
```

et pour les lancer avec un test de coverage et afficher le rapport :

```sh
coverage run -m pytest
coverage report
```

### Installer les hooks de pre-commit

Pour installer les git hook de pre-commit, installer le package precommit et installer les hooks en executant pre-commit

```sh
pip install pre-commit
pre-commit install
```

## Les API

Plus de détails sur la doc dédiée [SIAP-APiLos.md](./SIAP-APiLos.md)

## Ajouter des dépendances avec pip-tools

Ajouter les dépendances dans requirements.in ou dev-requirements.in

Puis compiler (recquiert l'installation de `pip-tools`):

```sh
make freeze-requirements
```

Et installer

```sh
pip install -r requirements.txt -r dev-requirements.txt
```

## Manipulations de développement

### Déclarer un superadmin

En local, éditer l'utilistateur en base de données pour lui assigner la valeur `is_superadmin` = true

Dans les autres environements, un superadmin a les droits pour déclarer les autres utilisateurs comme superadmin

### Modifier les permissions

Pour modifier les permissions, il suffit de modifier dans l'interface d'administration puis d'exporter les données d'authentification :

```sh
python manage.py dumpdata auth --natural-foreign --natural-primary > users/fixtures/auth.json
```

### Restaurer un dump de base de données

Afin de restaurer _proprement_ un fichier de dump de base de données, en supprimant au préalable les tables existantes,
on peut jouer le script suivant :

```bash
make db-restore
```

### Restaurer un dump sur un environnement Scalingo

**⚠️⚠️⚠️ Cette opération va supprimer les données sur l'environnement cible, n'executer cette commande que si vous êtes sûr de vous.**

Ouvrir un tunnel (cf. le dashboard de la base de données) :

```sh
DB_URL=postgres://<user>:<password>@<server>:<port>/<database>?sslmode=prefer
scalingo --app my-app db-tunnel --identity ~/.ssh/my_ssh_key $DB_URL
```

la commande retourne l'url d'accès à la base de données

```
Building tunnel to apilos-stag-3603.postgresql.dbs.scalingo.com:37228
You can access your database on:
127.0.0.1:10000
```

Dans un autre terminal, lancer la restauration

```sh
DB_URL=postgres://<user>:<password>@127.0.0.1:10000/<database>?sslmode=prefer
DUMP_FILE=</path/to/dump/file>
pg_restore -d "${DB_URL}" --clean --no-acl --no-owner --no-privileges "${DUMP_FILE}"
```

## MOCK CERBERE

En cas de non disponibilité de CERBERE en recette, il est possible de bouchonner l'authentification via CERBERE en définisant en variable d'environnement l'id de l'utilisateur à authentifier (à récupérer en base de données directement):

```sh
# Mock Cerbere user id - in case of CERBERE authentication failure
MOCK_CERBERE_USER_ID=
```

Si cette variable est définie, alors l'utilisateur est directement considéré comme authentifié et est utilisé pour récupérer les habilitations fournies par le SIAP.

⚠️ Ce mock est peu utilisé, il est possible qu'il ne soit pas fonctionnel

## Statistiques de développement

Pour suivre le travail et les performances de développement de l'équipe APiLos, On extrait régulièrement des statistiques en inspectant les releases et PR github.
Les indicateurs sont extraits et agrégés par mois :

* nb version majeur
* nb version mineur
* nb version de patch
* nb d'évolutions livrées
* nb de corrections livrées
* nb de mises à jour de dépendances
* nb de mises à jour technique
* nb de mises à jour de documentation
* nb d'escalades (demande de correction faite par l'équipe support suite à des retours des utilisateurs)
* nb de régressions (ça arrive :) )

Ces statistiques sont basées sur l'interprétation des numéros de release qui utilise la convention `semantic versionning` (vx.y.z, x majeur, y mineur, z patch) et sur l'inspection des tags des PR de chaque release : cela est possible car on utilise la fonction `squash and merge` de github lors de l'intégration de la PR sur la branche principale `main`, on a un commit par PR sur la branche main.

### Catégoriser les PR

Pour que le script d'extraction marche correctement, il est nécessaire de catégoriser les PR en les taguant avec les labels comme suit:

* bug
* enhancement
* documentation
* technical
* dependencies (tags déposé automatiquement par dépendadot lorsqu'il ouvre une PR)

Cette catégorisation est inspirée des labels proposés par défaut par Github

On ajoute aussi 2 labels en plus de cette catégorisation lorsque c'est approprié :

* escalation : quand la PR vient de notre processus d'escalade avec l'équipe Support
* regression : Pour le suivi des regressions

### Processus d'extraction des statistiques de developpement

Créer un token GitHub :

* Accéder à https://github.com
* Accéder au menu de votre profile
* Cliquer sur le menu `Settings`
* Cliquer sur le menu `Developper settings`
* Cliquer sur le menu `Personal access token` > `Tokens (classic)`
* Cliquer sur le bouton `Generate new token` > `Generate new token (classic)`
* Selectionner les options `public_repo`, `read:project`, `repo:status`, `repo_deployment`
* Créer le token et copier le

Lancer le script d'extraction des statistiques:

```sh
export GITHUB_TOKEN=<GITHUB_TOKEN>
python manage.py get_delivery_statistics --token $GITHUB_TOKEN --output DEV_STATISTICS.csv
```

Les statistiques de développement par mois sont disponibles dans le fichier `DEV_STATISTICS.csv`

## Mise à jour de la documentation technique

La documentation technique est maintenue dans la dossiers [docs](./docs) et elle est publiée avec la librairie python [sphynx](https://www.sphinx-doc.org/en/master/index.html)

les images sont stockées dans le répertoire [docs/_static](https://github.com/MTES-MCT/apilos/tree/main/docs/_static)

### Installation des librairie de génération de la documentation

```sh
pip install -r doc-requirements.txt
```

### Visualiser la documentation localement

Générer la documentation

```sh
rm -rf _build
sphinx-build -M html docs _build
```

La documentation est viualisable avec un navigateur à partir du fichier [_build/html/README.html](_build/html/README.html)
