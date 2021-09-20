# APiLos

> Assistance au Pilotage du Logement social

Plateforme Numérique pour la gestion unifiée des conventio APL

Lorsqu'un bailleur construit un logement social en france, avant la mise en location, il signe une convention APL avec le territoire.Ce tte conventionest nécéssaire

APiLos offre une solution numérique pour la gestion de ces convention entre bailleurs, territoire at plus tard d'autres acteur tel que les préfecture ou la CAF.

APiLos a aussi pour vocation d centraliser et fiabiliter les statistiques des logement sociaux sur le territoire français.

## Solution technique

Nous utilisons le framework Django.
Django
[Système de design de l'état](https://gouvfr.atlassian.net/wiki/spaces/DB/overview?homepageId=145359476)
... etc

### Linter

Nous utilisons [darker](https://github.com/akaihola/darker) pour gérer le formattage et le linter de l'application
Le fichier de configuration est pyproject.toml à la racine du projet

Pour installer les git hook de pre-commit, installer le package precommit

```
pip install pre-commit
```

et installer les hooks en executant pre-commit:

```
pre-commit install
```

## import SISAL

SISAL est le datawarehouse des APL dont nous exportons les données des agréments nécessaires au conventionnement APL

Pour faire cet import nous avons ajouté une commande django `import_galion` éditable ici : bailleurs/management/commands/import_galion.py

Pour executer cet import en local:

```docker-compose exec apilos python3 manage.py import_galion```

Sur Scalingo

```scalingo --app apilos-staging/fabnum-apilos run  python3 manage.py import_galion```


## liens utils

https://fabrique-numerique.gitbook.io/guide/developpement/etat-de-lart-de-lincubateur
https://doc.incubateur.net/startups/la-vie-dune-se/construction/kit-de-demarrage



## Pense-bête environnement technique

Dev : Django (comme Acceslibre, AideTerritoire TrackDechet)

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
