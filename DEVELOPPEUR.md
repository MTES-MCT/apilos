# DEVELOPPEMENT

Cette documentation décrit toutes les étapes nécessaires à l'intallation et au développement de la plateforme APiLos.

Les règles et standards de codage y sont décrits

## Installation local

La plateforme APiLos est open source et la gestion de version est assuré via Github. La première étape est donc de cloner ce repository github.

La gestion de dépendance est assurée via pipenv (cf. [Pipfile](Pipfile)).

Pour installer APiLos sur votre système en local, vous avez 2 possibilités :
* utiliser docker-compose
* utiliser pyenv

### Via docker-compose

#### Installation

Configurer vos variable d'environnement dans le fichier .env (exemple dans le fichier .env.template)

Toute l'application est disponible via docker-compose. L'avantage est l'isolation de la version de python et de la version de postgresql. Pas besoin d'installer un environment virtuel ni une version spécifique de postgresql, docker-compose le fait pour vous au plus proche des versions utilisées en production

Pour installer et lancer l'application,

```
docker-compose build
docker-compose up -d
```

Pensez à rebuilder le container docker lorsque vous ajouter une dépendance. les dépendances sont listées dans le fichier requirements.txt à la base du projet.

le code local est attaché au volume `/code/` à l'interieur du docker apilos. une seconde instance docker est executée pour la base de données. de même, les données de la base de données sont persisté car le dossier de données de la base de donnée est attaché en local dans un répéertoire pgdata ignoré par git.

Pour Lancer un script django, vous devrez l'éxecuter dans l'environnement docker en utilisant pipenv

```
docker-compose exec apilos pipenv run python manage.py ...
```

Par exemple pour lancer les migrations :

```
docker-compose exec apilos pipenv run python manage.py migrate
```

Enfin, pour afficher les logs :

```
docker-compose logs -f --tail=10
```

### Via pyenv



#### Installation
#### Lancement des tests

... todo

## Qualité de code

### Tests

Les tests sont organisés comme suit :
* Tests unitaires : APPNAME/tests/test_models.py
* Tests integration : APPNAME/tests/test_view.py
* Tests api : APPNAME/api/tests/test_apis.py


#### Lancement des tests avec docker-compose

L'application prend en charge des test unitaire et des tests d'intégration. Pour les lancer:

```
docker-compose exec apilos python manage.py test
```

et pour les lancer avec un test de coverage et afficher le rapport :

```
docker-compose exec apilos coverage run --source='.' manage.py test
docker-compose exec apilos coverage report
```

### Installer les hooks de pre-commit

TODO:
[] executer les hook de précommit dans docker si installation docker ?

Pour installer les git hook de pre-commit, installer le package precommit et installer les hooks en executant pre-commit

```
pip install pre-commit
pre-commit install
```


