```{toctree}
```

# Backup des buckets S3

Chaque semaine, on souhaite faire un backup du contenu des buckets s3 de production.
Pour executer ce back up on utilise github action

## Configuration

Pour s'exécuter, github action a besoin des identifiants s3 à configurer dans [Settings](https://github.com/MTES-MCT/apilos/settings) > Secrete > [Actions](https://github.com/MTES-MCT/apilos/settings/secrets/actions).

Ajouter les `Repository secrets` :

* S3_ACCESS_KEY
* S3_SECRET_KEY

## Execution

Le backup est exécuté régulièrement selon la configuraton du [workflow](../.github/workflows/s3_backup.yml)

Le résultat du backup est stocké dans les artefacts du workflow executé et est conservé 90 jours
