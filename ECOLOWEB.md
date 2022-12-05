# Migration des données depuis Ecoloweb

La migration des données depuis Ecoloweb se fait via une commande CLI (_command line interface_) de [Django](https://docs.djangoproject.com/fr/4.1/howto/custom-management-commands/).  

## Fonctionnement de la commande

La commande se nomme `import_ecoloweb_data` est lancée via Django (i.e. `manage.py`).  

Un accès en lecture seule à une base de données est nécessaire via la variable d'environnement `ECOLO_DATABASE_URL` qui
reste optionnelle sur le reste du projet.

L'ensemble des données importées au cours d'un lancement sont enregistrés au
sein d'une transaction SQL; soit tout est importé, soit rien. Il est cependant possible de ne pas utiliser de
transaction via l'option `--no-transaction`. En outre, un système de _références_ est mis en place pour éviter
d'importer 2 fois une donnée vers la base APiLos.

Pour lancer l'import des conventions sur un département, il faut ajouter le code INSEE de celui-ci en argument:

```bash
# Importer les données des Bouches du Rhône:
./manage.py import_ecoloweb_data 13
# Importer les données de la Haute Corse
./manage.py import_ecoloweb_data 2B
```

D'autres options, _réellement optionnelles_ celles-ci, sont disponibles:
* `--no-progress`: ne pas afficher la barre de progression dynamique (utile pour analyser les logs depuis Scalingo)
* `--debug`: affiche des informations supplémentaires au développeur (à conjuguer avec l'option `--no-progress`)

## Exécution de depuis Scalingo

Puisque le lancement d'un import sur un département peut durer entre plusieurs dizaines de minutes et quelques heures, il
va nous falloir suivre [la (très bonne) documentation concernant les "detached on-off" containers](https://doc.scalingo.com/platform/app/tasks).

Ex: pour lancer l'import des Bouches du Rhône :

```
scalingo --app <app> run --detached 'python ./manage.py import_ecoloweb_data 13 --no-progress'
```

Scaling va alors répondre avec un message comme suit :

```txt
Starting one-off 'python ./manage.py import_ecoloweb_data 13 --no-progress' for app '<app>'.
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

