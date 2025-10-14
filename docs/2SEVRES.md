# Cas pratique d'exhaustivité des 2 Sèvres

Un travail exceptionnel a été réalisé avec les instructeurs du département des 2 Sèvres.
Il s'agit de s'assurer de l'exhaustivité des données dans APiLos.

Les 2 Sèvres nous ont fournit un fichier Excel contenant toutes les données de l'ensemble des conventions du département connu par leur service.
Nous avons créé une commande de comparaison entre le fichier Excel et les données dans APiLos.
Nous nous sommes synchronisés une fois par mois pendant 4 à 5 mois le temps d'exécution du projet.

## Procédure d'extraction et de comparaison du fichier Excel avec APiLos

Sur un poste développeur, récupérer la base de production.

```bash
make db-restore
```

Lancer la commande de comparaison.

```bash
python manage.py compare_conventions_xlsx_vs_apilos --file /path/to/inventaire_conventionnement_79.xlsx
```

les résultats sont dans le même fichier excel :

- onglet "Resultats" : le matching entre le fichier Excel et APiLos, les cases en verts indique que la valeur est la même entre excel et DB APiLos, la colonne `Méthode de recherche de la convention` indique la méthode de recherche utilisée pour trouver la convention dans APiLos.
- onglet "Metadonnées" : nombre de conventions trouvées par type de recherche
- onglet "Conventions APiLos non trouvées" : les conventions trouvé dansla DB APilos mais pas dans le fichier Excel

## Conclusion du cas pratique

Le département des Deux Sèvres utilise maintenant exclusivement APiLos pour la gestion de leurs conventions.
Les conventions y sont exhaustives et ont été corrigées si nécessaire.
Les avenants ne sont pas exhaustifs mais à chaque fois qu'un avenant est nécessaire, l'instructeur•trice des Deux Sèvres vérifie que les avenants déclarés sur la convention sont exhautifs.
