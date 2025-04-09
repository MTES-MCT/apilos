```{toctree}
```

# Plan de continuité d'activité / Plan de reprise d'activité

## Prérequis

### Récupérer l'archive de la base de données

Si la base de données est à restaurer

Sur Scalingo, à parir de l'application à restaurer, accéder à l'archive de la base de données: `Ressources` / `Addons` / `PostgreSQL` / `Go to dashboard` / `BACKUPS`

Télécharger la dernière archive non comrompue.

### Récupérer le contenu du stockage s3

Si le stockage s3 est à restaurer.

Récupérer la dernière archive sur github (archivé tous les lundis matin):

- Accéder à la tâche github action qui archive les objets S3 : https://github.com/MTES-MCT/apilos/actions/workflows/s3_backup.yml
- Accéder à la dernière execution de la github action dont le contenu n'est pas comrompu
- Télécharger l'artefact s3_production

## Créaton d'un environnement sur le PaaS Scalingo

### Création de l'application

FIXME : qu'est-ce qu'est Scalingo

- Rendez-vous sur dashboard.scalingo.com
- Cliquer sur créer une application
- Créer une application avec le nom de votre choix, ex: "apilos-production"
- Choisir le déployement `Scalingo git server`
- Invitez vos collaborateurs sur le projet nouvellement créé `Settings` / `Collaborators`
Une fois les invitations acceptées, vous serez en capacité de transférer la propriété du projet, ceci transfert aussi la facturation

### Création de base de données

A partir de l'application sur Scalingo

- Accéder à la gestion des Addons `Ressources` / `Addons` / `Add an addon`
- Choisir PostgreSQL
- Choisir un plan (éviter le plan gratuit)
- Clicker sur `Provision Addons`

#### Création d'un utilisateur en lecture seule

Nécessaire pour le pluggin explorer de l'application

- Accéder à la gestion des utilisateurs de la base de données `Ressources` / `Addons` / `PostgreSQL` / `Go to dashboard` / `USERS`
- Créer un utilisateur en lecture seule sur la base de données
- Garder les identifiants, ils vous serviront pour configurer les variables d'environnement

#### Restoration de la base de donnée

- récupérer le DSN `SCALINGO_POSTGRESQL_URL` dans les variables d'environnement de votre nouvelle application
- Créer un tunnel ssh sur le réseau de votre application Scalingo (doc https://doc.scalingo.com/platform/databases/access), *Astuce : il faudra modifier l'URL et le port de la variable d'environnement `SCALINGO_POSTGRESQL_URL` en local avec les données fourni par le tunnel ssh*
- Restaurer la base de données avec la commande `pg_restore`, ex: pg_restore -d "${DB_URL}" --clean --no-acl --no-owner --no-privileges <dump_file.pgsql>
- Conseil, vérifier la présence des données sur la nouvelle base de données grâce à un client psql

### Sockage Objet S3

FIXME : stockage s3, pourquoi faire

#### Restoration du Sockage Objet S3

Accéder au fournisseur de stockage s3 (Scaleway)

- Créer un bucket `Stockage` / `Object Storage` / `Créer un bucket`
- Nommer le bucket
- Choisir un lieu de stockage
- Sélectionner la visibilité privé
- Activé le versionnage du bucket
- Dézipper l'archive
- Configurer un client aws s3 locallement pour accéder au bucket nouvellement créé (doc scaleway: https://www.scaleway.com/en/docs/storage/object/api-cli/object-storage-aws-cli/)
- Copier le contenu de l'archive dans le bucket

### Ajout d'un addon Redis

- Accéder à la gestion des Addons `Ressources` / `Addons` / `Add an addon`
- Choisir Redis
- Choisir un plan (éviter le plan gratuit)
- Clicker sur `Provision Addons`

## Deployer l'application

### Configurer les variables d'environnement

- Prenez le contenu de fichier [.env.template](https://github.com/MTES-MCT/apilos/blob/master/.env.template)
- Adapter les valeurs de chaque variable d'environnement pour l'environnement souhaité

### Déployer via le repositories git de Saclingo

Suivre la procédure de scalingo : https://doc.scalingo.com/platform/deployment/deploy-with-git

## Configurer

### Configurer les entrées DNS

Sur votre fournisseur de DNS (ex: alwaysdata)

- Ajouter le CName vers votre application Scalingo selon la documentation (https://doc.scalingo.com/platform/app/domain#configure-your-domain-name)

### Adapté la configuration réseau sur Scalingo

A partir de l'application sur Scalingo

- Accéder aux paramètres réseau de l'application `Settings` / `Domains / SSL` / `Add`
- Ajouter l'URL de l'application
- Modifier la configuration SSL dans `Settings` / `Routing`
- Activé l'option `Force HTTPS`
- Modifier la variable d'environnement `ALLOWED_HOSTS` pour ajouter l'url de l'application


## Architecture double : SIAP et Webapp indépendante

La WebApp APiLos est déployée 2 fois, 1 dépendante du SIAP et 1 indépendante, cf. [Architecture APiLos](https://github.com/MTES-MCT/apilos#solution-technique)

Il sera donc peut-être nécessaire d'appliquer la procédure ci-dessus 2 fois excepté pour les briques logiciel qui sont partagées:
- Base de données PostgreSQL
- Stockage Object S3
- La variable d'environnement `ENVIRONMENT`
