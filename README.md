# APiLos

> Assistance au Pilotage du Logement social

Plateforme Numérique pour la gestion unifiée des conventions APL

Lorsqu'un bailleur construit un logement social en france, avant la mise en location, il signe une convention APL avec le territoire. Cette convention est nécéssaire pour déterminer le prix au m2 et d'autres modalités de mise en location.

APiLos offre une solution numérique pour la gestion de ces conventions entre bailleurs et instructeur de l'état (appartenant généralement au territoire) et plus tard d'autres acteurs tel que les préfectures ou la CAF.

APiLos a aussi pour vocation de centraliser et fiabiliter les statistiques des logemente sociaux sur le territoire français pour un pilotage éclairé de la construction du parc social en France.

APiLos est un produit du SIAP (Système d'information des aides à la pierre)

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

### Installation de la plaeforme en local (Developpeurs)

[DEVELOPPEUR.md](DEVELOPPEUR.md)

### Déploiement (Staging et Production)

[DEPLOIEMENT.md](DEPLOIEMENT.md)

### CI/CD et branch git

Les "User Stories" (US) sont développées sur des "feature branches" (convention de nommage sNUM-US_DESCRIPTION) à partir de la branch `develop`.
les `feature branches` font l'objet de `pull request` à merger sur `develop`.
les `releases` sont préparées et déployées à partir de ma branch `master`

La solution circleci est utilisée: [CircleCI:Apilos](https://app.circleci.com/pipelines/github/MTES-MCT/apilos?filter=all)
La config est ici : [.circleci/config.yaml](.circleci/config.yaml)

#### CI

A chaque push sur github, le projet est buildé et les tests sont passés

#### CD

A chaque push sur la branche `develop`, le projet est déployé en [staging](https://staging.apilos.incubateur.net/)

### Déploiement

Lors du déploiement, les étapes définient dans le script [bin/post_deploy](bin/post_deploy) sont éxécutées:

1. Execution des migrations de la base de données
2. Population des roles et des permissions
3. Suppression des sessions expirées

### Déploiement en staging

Pour déployer en staging, il suffit de pousser le code sur le repository git de scalingo dans le projet de staging

```git push git@ssh.osc-fr1.scalingo.com:fabnum-apilos.git master:master```

### Déploiement en production

A faire : intégrer le process de mise en prod dans circle ci

Pour pousser en production, la version à pousser en production doit être préparée sur la branche `master` soit en mergeant les développements de la branche `develop`, soit à l'aide de la commande `cherry-pick`

La branche `master` doit-être pousser sur le repo origin pour que les tests soient executés avant que la branche soit déployée

Puis la la branche `master` peut-être déployée sur l'environnement de `production` sur scalingo avec la commande :

```git push git@ssh.osc-fr1.scalingo.com:fabnum-apilos.git master:master```

### import SISAL

SISAL est le datawarehouse des APL dont nous exportons les données des agréments nécessaires au conventionnement APL

Pour faire cet import nous avons ajouté une commande django `import_galion` éditable ici : bailleurs/management/commands/import_galion.py

Pour executer cet import en local:

```docker-compose exec apilos pipenv run python3 manage.py import_galion```

Sur Scalingo

```scalingo --app apilos-staging/fabnum-apilos run  python3 manage.py import_galion```

### Populer les permissions

Pour modifier les permissions, il suffit de modifier dans l'interface d'administration puis d'exporter les données d'authentification :

```docker-compose exec apilos pipenv run python manage.py dumpdata auth --natural-foreign --natural-primary > users/fixtures/auth.json```

et pour populer ces données :

```docker-compose exec apilos pipenv run python manage.py loaddata auth.json```

Cette commande est excutée lors du déploiement de l'application juste après la migration

### Envoie de mails

Nous utilisons mailjet. Si les variables d'environnements MAILJET_API_KEY et MAILJET_API_SECRET sont configurées, le backend email Mailjet est utilisé. Sinon, le backend email console est utilisé et les mail sont imprimé dans a console (dans les logs)

### DNS

Les DNS sont configurés dans always data

### Mailing list

Les mailing lists sont configurées dans alwaysdata. Nous utilisons uniquement la mailing list contact@apilos.beta.gouv.fr.

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
