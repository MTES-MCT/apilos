# APpeL

Plateforme Numérique pour la gestion unifiée des conventio APL

Lorsqu'un bailleur construit un logement social en france, avant la mise en location, il signe une convention APL avec le territoire.Ce tte conventionest nécéssaire

APpeL offre une solution numérique pour la gestion de ces convention entre bailleurs, territoire at plus tard d'autres acteur tel que les préfecture ou la CAF.

APpeL a aussi pour vocation d centraliser et fiabiliter les statistiques des logement sociaux sur le territoire français.

## Solution technique

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

## liens utils

https://fabrique-numerique.gitbook.io/guide/developpement/etat-de-lart-de-lincubateur
https://doc.incubateur.net/startups/la-vie-dune-se/construction/kit-de-demarrage



## Pense-bête environnement technique

Dev : Django (comme Acceslibre, AideTerritoire TrackDechet)

Tests unitaires et integration
CI/CD: github-action / circleci ?
Base documentaire : S3 avec scaleway
PAAS - Scalingo
Analytics : Matomo
Monitoring logiciel : Sentry
Monitoring système : updownio ?
Monitoring securité : dashloard

Protection des données :
Pensez aux CGU et compatibilité RGPD

Etape du projet à venir (plus tard) : Audit de securité des données

Monitoring des métriques métiers :
Statistique projet : path /stats - statistiques faisant preuve de la réussite du projet
