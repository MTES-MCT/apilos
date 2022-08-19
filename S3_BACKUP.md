# Backup des buckets S3

Chaque semaine, on souhaite faire un backup du contenu des buckets s3 de production.
Pour executer ce back up on utilise github action

## Configuration

Pour s'exécuter, github action a besoin des identifiants s3 à configurer dans [Settings](https://github.com/MTES-MCT/apilos/settings) > Secrete > [Actions](https://github.com/MTES-MCT/apilos/settings/secrets/actions).

Dans la section environnement secrets, ajouter les clés:
* S3_ACCESS_KEY
* S3_SECRET_KEY

