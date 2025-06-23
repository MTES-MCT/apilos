# Services tiers utilisés par APiLos

APiLos utilise un certain nombre de servce tiers pour fonctionner.L'équipe technique d'APiLos doit avoir un compte pour chacun de ces services.

- Scalingo (hébergement) : PaaS souverain. Voir le responsable technique du service responsable du marché pour créer les accès aux développeurs. Les projets actifs sur Scalingo sont :
  - apilos-ecolo (image de la base de données Ecoloweb, peu/pas utilisé)
  - apilos-metabase-prod (metabase)
  - clamav-service (Antovirus as a service)
  - apilos-siap-integration (Plateforme d'intégration)
  - apilos-siap-recette (Plateforme de recette - utilisée par l'équipe SIAP)
  - apilos-siap-ecole (plateforme école - utilisée par l'équipe SIAP)
  - apilos-siap-production (Plateforme de production)

- GitHub (https://github.com/MtES-MCT/apilos/) - gestion par FabNum/DNUM : Gestion des versions du code d'APiLos. Publié en open-source.

- S3 sur Scaleway - Géré par Nicolas O. : Stockage des documents de convention et des documents attachés aux convention. Le stockage S3 sera prochainement migrée sur une solution s3 maîtrisé par la FabNum/DNUM

- Sentry (fournit par beta.gouv.fr) - géré par beta.gouv.fr et FabNum/DNUM : Monitoring logiciel d'APiLos

- Dashlord/UpDown.io géré FabNum/DNUM : Monitoring système et qualité de APiLos

- Alwaysdata (gestion des DNS - compte Nicolas Oudard) : tous les environnements sauf la production sont sous le domaine apilos.beta.gouv.fr. Les URLs de ces environnements seront prochainement modifiées pour ne plus dépendre du sous domaine beta.gouv.fr
