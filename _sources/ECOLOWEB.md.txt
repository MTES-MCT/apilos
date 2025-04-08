```{toctree}
```

# Migration des données depuis Ecoloweb

La migration des données depuis Ecoloweb se fait via une commande CLI (_command line interface_) de [Django](https://docs.djangoproject.com/fr/4.1/howto/custom-management-commands/).

## Installation de la base de données

Les exports de données nous sont transmis au format `.pgsql`. Pour pouvoir les charger
sur la base @ Scalingo, le seul moyen stable est de [créer un tunnel SSH](https://doc.scalingo.com/platform/databases/access#encrypted-tunnel).
Une fois celui-ci en place, il reste à supprimer les tables existantes et importer
le fichier de dump:

```bash
DB_URL=postgres://<user>:<password>@localhost:10000/<dbname>

for table in $(psql "${DB_URL}" -t -c "SELECT \"tablename\" FROM pg_tables WHERE schemaname='ecolo'"); do
     psql "${DB_URL}" -c "DROP TABLE IF EXISTS \"${table}\" CASCADE;"
done
pg_restore -d "${DB_URL}" --clean --no-acl --no-owner --no-privileges <fichier_dump>.pgsql
```

## Structure des données @ Ecoloweb

Sur Ecoloweb, les informations clefs et pérennes d'une convention sont gardées _éternellement_ dans la table `ecolo_conventionapl`.
On y trouve par exemple le numéro, l'administration qui en est à l'origine et globalement toutes les infos inaltérables.

Pour autant une convention évolue avec le temps, en étant soit _reconduite_ sur une nouvelle période, soit _altérée_ via
un **avenant**. Chaque altération crée une nouvelle entrée dans la table `ecolo_conventiondonneesgenerales`. Ces données
générales incluent les dates de début et de fin, une éventuelle référence vers la table `ecolo_avenant`, toutes les
dates d'évènements d'envoi, signature, publication ou encore le notaire ou le bureau CAF concerné. Surtout, à chaque
_donnée générale_ sont associées des `ecolo_programmelogement`, eux-mêmes constitués de `ecolo_logement` et `ecolo_annexe`,
soit plus largement des infos détaillant _le contenu_ de ce qui est conventionné.

On peut donc obtenir rapidement le détail de toutes les altérations successives d'une convention en examinant le contenu
derrière chaque _donnée générale_ liée à une même `ecolo_conventiondonneesgenerales.conventionapl_id`.

## Fonctionnement de la commande

La commande se nomme `ecoloweb_import_departement` est lancée via Django (i.e. `manage.py`).

Un accès en lecture seule à une base de données est nécessaire via la variable d'environnement `ECOLO_DATABASE_URL` qui
reste optionnelle sur le reste du projet.

L'ensemble des requêtes effectuées au cours d'un import n'est _pas_ joué au sein d'une transaction SQL. Il est cependant
possible de le faire via l'option `--use-transaction`. En outre, un système de _références_ est mis en place pour éviter
d'importer 2 fois une donnée vers la base APiLos.

Pour lancer l'import des conventions sur un département, il faut ajouter le code INSEE de celui-ci en argument:

```bash
# Importer les données des Bouches du Rhône:
./manage.py ecoloweb_import_departement 13
# Importer les données de la Haute Corse
./manage.py ecoloweb_import_departement 2B
```


D'autres options, _réellement optionnelles_ celles-ci, sont disponibles:
* `--no-progress`: ne pas afficher la barre de progression dynamique (utile pour analyser les logs depuis Scalingo)
* `--debug`: affiche des informations supplémentaires au développeur (à conjuguer avec l'option `--no-progress`)
* `--setup`: supprime et recrée la _materialized view_ `ecolo_conventionhistorique`, en charge
de retranscrire l'historique Ecolo vers celui d'Apilos. Comme cette étape est assez longue, cette
option n'est utile qu'après un changement de structure de cette _view_ **ou** après l'import d'un
dump de base de données Ecolo
* `--update`: si une convention a déjà été importée depuis Ecolo, et non supprimée depuis, cette option
force la mise à jour des données sur Apilos avec celles issues d'Ecoloweb (⚠️ tout changement survenu entre
temps sera écrasé)
## Exécution de depuis Scalingo

Puisque le lancement d'un import sur un département peut durer entre plusieurs dizaines de minutes et quelques heures, il
va nous falloir suivre [la (très bonne) documentation concernant les "detached on-off" containers](https://doc.scalingo.com/platform/app/tasks).

Ex: pour lancer l'import des Bouches du Rhône :

```sh
scalingo --app <app> run --detached 'python ./manage.py ecoloweb_import_departement 13 --no-progress'
```

Scaling va alors répondre avec un message comme suit :

```
Starting one-off 'python ./manage.py ecoloweb_import_departement 13 --no-progress' for app '<app>'.
Run `scalingo --region <region> --app <app> logs --filter one-off-<number>` to get the output
```

Le processus est ainsi lancé jusqu'à la fin de l'import qui fermera le conteneur.

On peut malgré tout toujours opérer dessus :

```bash
# Afficher les conteneurs en cours:
scalingo --app <app> ps
# Voir les logs du conteneur:
scalingo --app <app> logs --filter one-off-<number> -f
# Stopper manuellement le conteneur:
scalingo --app <app> one-off-stop one-off-<number>
```

## Tests unitaires

2 prérequis sont nécessaires pour pouvoir exécuter les tests unitaires:
1. déclarer un accès à la base de données Ecoloweb via la variable `ECOLOWEB_DB_URL`
2. ramener depuis le bucket S3 dédié les fichiers SQL de création et d'alimentation de cette base de données

Pour cette seconde étape, il faut au préalable utiliser [la commande `aws`](https://aws.amazon.com/fr/cli/) pour récupérer
la version la plus à jour:

```bash
aws s3 sync <S3_BUCKET> ecoloweb/tests/resources/
```

Ce bucket est structuré de cette façon:
* un répertoire `sql` contenant toutes les requêtes de création des tables (`ddl` ou _Data Definition Language_) ainsi
que l'alimentation de celles-ci (`dcl` ou _Data Creation Language_)
* un autre répertoire `sources` contenant les requêtes qui ont permis l'extraction de certaines données depuis une source
existante. Ces requête sont utiles pour isoler les requêtes de _DCL_, en conjonction de la fonction d'"Export as SQL inserts"
des IDEs Jetbrain

Si jamais vous éditez ces fichiers, pensez à bien les synchroniser sur le bucket S3:

```bash
aws s3 sync --delete ecoloweb/tests/resources/ <S3_BUCKET>
```

## Retrouver une convention dans Ecoloweb

```sh
# se connecter à la base de données via le CLI Scalingo
scalingo -a <app> pgsql-console
```

À noter : `\dt` ne retourne aucune table, c'est *normal*.


### Retrouver le statut d'une convention

Par exemple à partir de l'uuid d'une convention, en se connectant au django shell
```shell
from conventions.models import Convention
from ecoloweb.models import EcoloReference

convention_id = Convention.objects.get(uuid="c8e67014-14db-4cb2-bd28-6db24bb6cabc").id
EcoloReference.objects.get(apilos_model="conventions.Convention", apilos_id=convention_id).ecolo_id
# '12345678:PLAI:0'
```

Dans l'exemple ci-dessus, le première partie de l'id avant le premier `:` est à utiliser dans la requête ci-dessous :
```sql
SELECT vps.*
from ecolo.ecolo_conventionhistorique ch
    inner join ecolo.ecolo_conventiondonneesgenerales cdg on cdg.id = ch.conventiondonneesgenerales_id
    inner join ecolo.ecolo_valeurparamstatic vps on vps.id = cdg.etatconvention_id
where ch.conventionapl_id = '12345678';

```
