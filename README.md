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

Les DNS sont configurés dans [Alwaysdata](https://admin.alwaysdata.com/)
les emails et mailing list sous le domaine apilos.beta.gouv.fr sont aussi géré avec Alwaysdata : contact@apilos.beta.gouv.fr, recrutement@apilos.beta.gouv.fr, staff@apilos.beta.gouv.fr

### Bases de données

![apilos_db](static/img/apilos_db.svg)

### Stockage de fichiers

Les documents sont stockés sur un répertoire distant et souverain compuatible avec le protocole S3 sur [Scaleway](https://console.scaleway.com/object-storage/buckets)

La librairie python boto en combinaison avec le package default_storage de Django

Ce stockage est activé lorsque les variable d'environnement AWS... sont définit. La configuration est faite dans core/settings.yml

```
   DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
```

### Analytics

APilos utilise [Matomo](https://stats.data.gouv.fr/index.php?module=CoreHome&action=index&idSite=188&period=day&date=yesterday#?idSite=188&period=day&date=yesterday&segment=&category=Dashboard_Dashboard&subcategory=1) comme outils d'analytics sous le domaine stats.data.gouv.fr

### Monitoring logiciel

Nous utilisons [Sentry](https://sentry.io/organizations/betagouv-f7/issues/?project=5852556) fournit par beta.gouv.fr

### Monitoring système

APiLos est monitoré par l'outils [Dashlord](https://dashlord.mte.incubateur.net/dashlord/url/apilos-beta-gouv-fr/) de la fabrique du numérique du ministère de la transition écologique

Monitoring système : updownio ?

## Protection des données :

Les CGU sont publiés [sur le site APiLos](https://apilos.beta.gouv.fr/cgu) et inclus les obligations relatives au RGPD
Le rapport d'accessibilité est publié [sur le site APiLos](https://apilos.beta.gouv.fr/accessibilite)

## Statistique de la plateforme

Les statistiques d'usage et le suivi des KPIs de la start up d'état sont disponibles sur la [page de statistique](https://apilos.beta.gouv.fr/stats)

## liens utils

https://fabrique-numerique.gitbook.io/guide/developpement/etat-de-lart-de-lincubateur
https://doc.incubateur.net/startups/la-vie-dune-se/construction/kit-de-demarrage
