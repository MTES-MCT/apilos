# APiLos

> Assistance au Pilotage du Logement social

Plateforme Numérique pour la gestion unifiée des conventions APL

Lorsqu'un bailleur construit un logement social en france, avant la mise en location, il signe une convention APL avec le territoire. Cette convention est nécéssaire pour déterminer le prix au m2 et d'autres modalités de mise en location.

APiLos offre une solution numérique pour la gestion de ces conventions entre bailleurs et instructeur de l'état (appartenant généralement au territoire) et plus tard d'autres acteurs tel que les préfectures ou la CAF.

APiLos a aussi pour vocation de centraliser et fiabiliter les statistiques des logemente sociaux sur le territoire français pour un pilotage éclairé de la construction du parc social en France.

## Solution technique

La plateforme est développé avec le framework Django et son moteur de template par défaut.

Le design de l'interface suit le [Système de design de l'état](https://gouvfr.atlassian.net/wiki/spaces/DB/overview?homepageId=145359476)

La génération de document .docx est prise en charge par la librairie [python-docx-template](https://docxtpl.readthedocs.io/en/latest/) qui utilise le moteur de template Jinja2 pour générer des documents docx

Le package openpyxl est utilisé pour l'interprétation des fichier xlsx

### Qualité de code

Plusieurs outils sont utilisés pour gérer la qualité de code:

* [git pre-commit](https://pre-commit.com/) avec les hooks de bases : trailing-whitespace, check-yaml, check-added-large-files
* [pylint](https://pypi.org/project/pylint/) comme linter intégré au pre-commit pour les fichier python (config $BASE/.pylintrc)
* [djhtml](https://pypi.org/project/djhtml/) comme prettier des fichiers html
* [black](https://pypi.org/project/black/) comme prettier des fichiers python


### Installer les hook de pre-commit

Pour installer les git hook de pre-commit, installer le package precommit

```
pip install pre-commit
```

et installer les hooks en executant pre-commit:

```
pre-commit install
```

## Installation et déploiement

### Installation local pou déveloper

Configurer vos variable d'environnement dans le fichier .env (exemple dans le fichier .env.template)

Toute l'application est disponible via docker-compose. L'avantage est l'isolation de la version de python et de la version de postgresql. Pas besoin d'installer un environment virtuel ni une version spécifique de postgresql, docker-compose le fait pour vous au plus proche des versions utilisées en production

Pour installer,

```
docker-compose build
```

Pensez à rebuilder le container docker lorsque vous ajouter une dépendance. les dépendances sont listées dans le fichier requirements.txt à la base du projet.

Pour lancer l'application en local

```
docker-compose up -d
```

Lancer un script django

```
docker-compose exec apilos python manage.py ...
```

Par exemple pour lancer les migrations :

```
docker-compose exec apilos python manage.py migrate
```

Afficher les logs

```
docker-compose logs -f --tail=10
```

### Lancement des tests

```
docker-compose exec apilos python manage.py test
```

#### Coverage

Lancé un test coverage

```
docker-compose exec apilos coverage run --source='.' manage.py test
```

Consulté le raport de coverage

```
docker-compose exec apilos coverage report
```

### CI/CD

La solution circleci est utilisée. La config est ici : $BASE/.circleci/config.yaml

#### CI

A chaque push sur github, le projet est buildé et les tests sont passés

#### CD

A chaque push sur la branche develop, le projet est déployé en [staging](https://staging.apilos.incubateur.net/)

### Push to prod

A faire : intégrer le process de mise en prod dans circle ci

En attendant, utiliser la commande à partir de la branch master : `git push git@ssh.osc-fr1.scalingo.com:fabnum-apilos.git master:master`

### import SISAL

SISAL est le datawarehouse des APL dont nous exportons les données des agréments nécessaires au conventionnement APL

Pour faire cet import nous avons ajouté une commande django `import_galion` éditable ici : bailleurs/management/commands/import_galion.py

Pour executer cet import en local:

```docker-compose exec apilos python3 manage.py import_galion```

Sur Scalingo

```scalingo --app apilos-staging/fabnum-apilos run  python3 manage.py import_galion```

### Envoie de mails

Nous utilisons mailjet. Si les variables d'environnements MAILJET_API_KEY et MAILJET_API_SECRET sont configurées, le backend email Mailjet est utilisé. Sinon, le backend email console est utilisé et les mail sont imprimé dans a console (dans les logs)

### Mailing list

Les mailing lists sont configurées dans alwaysdata.

## liens utils

https://fabrique-numerique.gitbook.io/guide/developpement/etat-de-lart-de-lincubateur
https://doc.incubateur.net/startups/la-vie-dune-se/construction/kit-de-demarrage



## Pense-bête environnement technique


Tests unitaires et integration
Base documentaire : S3 avec scaleway
Analytics : Matomo
Monitoring logiciel : Sentry
Monitoring système : updownio ?
Monitoring securité : dashloard

Protection des données :
Pensez aux CGU et compatibilité RGPD

Etape du projet à venir (plus tard) : Audit de securité des données

Monitoring des métriques métiers :
Statistique projet : path /stats - statistiques faisant preuve de la réussite du projet
