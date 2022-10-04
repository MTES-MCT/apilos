# DEPLOIEMENT DE LA PLATEFORME APILOS

## Solution d'hébergement

La solution souveraine PaaS de [Scalingo](https://dashboard.scalingo.com/apps/osc-fr1/fabnum-apilos) est utilisée avec les composants suivants :
* webapp : Application Django incluant interface et APIs, la webapp est déployé un système Ubunti 20.x
* Une base de données postgres en version 12.7.0

La base de données est backupée toute les nuits et Scalingo propose une solution PITR (Point-in-time recovery) pour sa restauration

## CI/CD et branch git

Les "User Stories" (US) sont développées sur des "feature branches" (convention de nommage sNUM-US_DESCRIPTION) à partir de la branch `develop`.
les `feature branches` font l'objet de `pull request` à merger sur `develop`.
les `releases` sont préparées et déployées à partir de ma branch `master`

La solution circleci est utilisée: [CircleCI:Apilos](https://app.circleci.com/pipelines/github/MTES-MCT/apilos?filter=all)
La config est ici : [.circleci/config.yaml](.circleci/config.yaml)

### CI

A chaque push sur github, le projet est buildé et les tests sont passés

### CD

A chaque push sur la branche `develop`, le projet est déployé en [staging](https://staging.apilos.incubateur.net/)

## Déploiement

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

## Déployer un nouvel environnement

1. ajout d'une application dans scalingo
1. Ajout d'addons : postgresql, redis
1. Ajout des variable d'environnement (Scalingo > Environnement)
1. Ajout du nom de domaine dans scalingo (Scalingo > Settings > Domain/SSL)
1. Ajout d'un enregistrement DNS CNAME vers l'APP Scalingo (Alwaysdata > Domains > DNS Records)
1. Forcer HTTPS (Scalingo > Settings > Routing)
1. Scale les APPs (Scalingo > Resources)
1. Créer le bucket sur scaleway

Pour le SIAP,

9. Créer un utilisateur siap et transmettre son id au équipe du SIAP

# Déploiement de Metabase

Suivre les instructions de la doc de l'incubateur :

https://doc.incubateur.net/communaute/travailler-a-beta-gouv/jutilise-les-outils-de-la-communaute/metabase

Pour mettre à jour

```
scalingo --app apilos-metabase-prod deploy https://github.com/Scalingo/metabase-scalingo/archive/refs/heads/master.tar.gz
```

Quelques informations complémentaires:
* Metabase est installé sur le projet `apilos-metabase-prod` sur scalingo
* L'installation de Metabase nécessite une base de données accessible en écriture. Nous avons doc fait le choix de créer une DB dédié à Métabase comme addon du projet `apilos-metabase-prod` sur scalingo, celle-ci sert à l'administration de Metabase, les infomations de connection à la base de données sont accessible sur scalingo e interprétant la variable d'environnement SCALINGO_POSTGRESQL_URL
* La base de données APiLos est configurée dans l'administration de Metabase et a un accès en Lecture seule
* Les données stockées par Metabase sont cryptées grâce à la variable d'environnement MB_ENCRYPTION_SECRET_KEY
* les données SMTP sont celles du compte email de nicolas.oudard@beta.gouv.fr

Metabase est ccessible à l'adresse [https://apilos-metabase-prod.osc-fr1.scalingo.io/]()
