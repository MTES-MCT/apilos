# DEVELOPPEMENT

Cette documentation décrit toutes les étapes nécessaires à l'intallation et au développement de la plateforme APiLos.

Les règles et standards de codage y sont décrits

## Installation

La plateforme APiLos est open source et la gestion de version est assuré via Github. La première étape est donc de cloner ce repository github.

### Prérequis

Les services Postgresql et Redis utilisés par APiLos sont dockerisés
Python et Node sont nécessaires pour faire lacer l'application
Il est conseillé d'installer un environnment virtuel pour isoler l'environnement python et node d'APiLos (asdf par exemple)

- Python >=3.10
- Node >=18.14
- docker
- docker-compose

### Environment virtuel python

```sh
python -m venv .venv --prompt $(basename $(pwd))
source .venv/bin/activate
```

### Services docker

```sh
docker-compose build
docker-compose up -d
```

### Variables d'environnement

Copier les [.env.template](.env.template) dans un fichier `.env` et [.env.test](.env.test) dans `.env.test.local` puis mettre à jour les variables d'environements.

```sh
cp .env.template .env
cp .env.test .env.test.local
```

Par exemple:

```ini
DB_USER=apilos
DB_NAME=apilos
DB_HOST=localhost
DB_PASSWORD=apilos
DB_PORT=5433
```

### Installer les dépendances python

```sh
pip install pip-tools
pip install -r requirements.txt -r dev-requirements.txt
```

### Installer les dependances npm

```sh
npm install
```

### Executer les migrations

```sh
python manage.py migrate
```

### Populer les permissions et les roles et les departements

```sh
python manage.py loaddata auth.json departements.json
```

#### Modifier les permissions

Pour modifier les permissions, il suffit de modifier dans l'interface d'administration puis d'exporter les données d'authentification :

```sh
python manage.py dumpdata auth --natural-foreign --natural-primary > users/fixtures/auth.json
```

### Créer un super utilisateur

```sh
python manage.py createsuperuser
```

## Lancer de l'application

```sh
python manage.py runserver 0.0.0.0:8001
```

L'application est désormais disponible [http://localhost:8001](http://localhost:8001)

### Population de la base de donnnées en environnement de développement

Ajout les bailleurs, administrations, programmes, lots, logements, types de stationnement issue galion

```sh
python manage.py import_galion
```

Ajout de bailleurs, administrations, programmes et lots de test

```sh
python manage.py load_test_fixtures
```

## Qualité de code

### Tests

Les tests sont organisés comme suit :

- Tests unitaires : APPNAME/tests/models/…
- Tests integration : APPNAME/tests/views/… APPNAME/tests/services/…

### Lancement des tests

L'application prend en charge des test unitaire et des tests d'intégration. Pour les lancer:

```sh
python manage.py test
```

et pour les lancer avec un test de coverage et afficher le rapport :

```sh
coverage run --source='.' manage.py test
coverage report
```

### Installer les hooks de pre-commit

Pour installer les git hook de pre-commit, installer le package precommit et installer les hooks en executant pre-commit

```sh
pip install pre-commit
pre-commit install
```

## Les API

Plus de détails sur la doc dédiée [API.md](API.md)

## Ajouter des dépendances avec pip-tools

Ajouter les dépendances dans requirements.in ou dev-requirements.in

Puis compiler (recquiert l'installation de `pip-tools`):

```sh
pip install pip-tools
pip-compile --resolver=backtracking requirements.in --generate-hashes
pip-compile --resolver=backtracking dev-requirements.in --generate-hashes
```

Et installer

```sh
pip install -r requirements.txt -r dev-requirements.txt
```

## Manipulations de développement

### Restaurer un dump de base de données

Afin de restaurer _proprement_ un fichier de dump de base de données, en supprimant au préalable les tables existantes,
on peut jouer le script suivant :

```bash
DUMP_FILE=</path/to/dump/file>
DB_URL=postgres://apilos:apilos@localhost:5433/apilos

for table in $(psql "${DB_URL}" -t -c "SELECT \"tablename\" FROM pg_tables WHERE schemaname='public'"); do
     psql "${DB_URL}" -c "DROP TABLE IF EXISTS \"${table}\" CASCADE;"
done
pg_restore -d "${DB_URL}" --clean --no-acl --no-owner --no-privileges "${DUMP_FILE}"
```

Note : le fichier de dump est a l'extension `pgsql`

### Restaurer un dump sur un environnement Scalingo

**⚠️⚠️⚠️ Cette opération va supprimer les données sur l'environnement cible, n'executer cette commande que si vous êtes sûr de vous.**

Ouvrir un tunnel (cf. le dashboard de la base de données) :

```sh
DB_URL=postgres://<user>:<password>@<server>:<port>/<database>?sslmode=prefer
scalingo --app my-app db-tunnel --identity ~/.ssh/my_ssh_key $DB_URL
```

la commande retourne l'url d'accès à la base de données

```txt
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

## Utilisateurs

L'import des fixtures crée plusieurs utilisateurs utiles lors du développement

|             | identifiant      | mot de passe | email                       |
|-------------|------------------|--------------|-----------------------------|
| bailleur    | demo.bailleur    | demo.12345   | demo.bailleur@oudard.org    |
| instructeur | demo.instructeur | instru12345  | demo.instructeur@oudard.org |

## Commandes

Certaines [commandes Django](https://docs.djangoproject.com/fr/4.2/ref/django-admin/) ont été décrites, et peuvent être executées en local ou sur un serveur de production.

### `./manage.py remove-duplicate-siap-users`

Supprime les comptes des utilisateurs de la plateforme autonome si ils disposent d'un compte APiLos en version SIAP.

Options :

- **--dry-run** : exécute la commande sans rien écrire en base de données
- **--verbose** : affiche la liste des utilisateurs à supprimer
