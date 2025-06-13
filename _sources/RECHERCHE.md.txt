```{toctree}
```

# Recherche de conventions

La recherche de conventions est la page d'accueil d'APiLos. Elle permet de retrouver une convention selon différents critères.

## Principe de la recherche

Pour effectuer une recherche, l'utlisateur remplit le formulaire en haut de la page `/recherche`.

Après avoir complété le formulaire, la page de recherche va se recharger avec des query params supplémentaires dans l'url. Ces params sont des filtres qui vont être appliqués sur l'ensemble des conventions visibles pour l'utilisateur pour ne conserver que le résultat de la recherche.

Exemple si on recherche un numéro de convention `1234` en staging, l'url de la page devient `https://siap-integration.apilos.beta.gouv.fr/conventions/recherche?order_by=&page=&search_operation_nom=&search_numero=1234&bailleur=&search_lieu=&cstatut=&financement=&date_signature=&nature_logement=`. La plupart des paramètres sont vides, mais on trouve `search_numero=1234`. Le résultat d'une recherche est ainsi matérialisé par une url, mais attention, les conventions sont préalablement filtrées selon les habilitations de l'utilisateur. Deux utilisateurs consultant la même url de recherche ne verront pas les mêmes résultats, mais les mêmes filtres seront appliqués à leurs conventions visibles.

La logique de la recherche est située dans `conventions/services/search.py`.

## Liste des filtres disponibles

| Champ du formulaire | Filtre (en query param) |
| ------------------- |-------------|
| Nom de l'opération | search_operation_nom |
| Numéro de l'opération ou de la convention  | search_numero |
| Bailleur (nom ou SIREN) | bailleur |
| Commune, code postal | search_lieu |
| Statut convention ou avenant | cstatut |
| Type de financement | financement |
| Année de signature | date_signature |
| Nature des logements | nature_logement |

## Ordre de la recherche

L'ordre présenté à l'utilisateur inclut deux paramètres : le score et la date de création de la convention. Le score est déterminé par `_build_scoring`, qui normalise le ranking déterminé par `_build_ranking`.

Différentes méthodes ont été testées empiriquement pour déterminer le ranking, des champs utilisent `TrigramSimilarity`, d'autres `SearchRank`. Le scoring rend comparable ces rankings obtenus par des méthodes différentes.

## Filtre via les habilitations

L'échantillon de conventions sur lequel les filtres sont appliqués est obtenu par la méthode `conventions` du modèle User, qui se charge de réduire l'échantillon aux conventions visibles par l'utilisateur.

En général quand un utilisateur se plaint de ne pas retrouver une convention dans la recherche, c'est lié à des données géographiques qui ne concordent pas entre la convention et les habilitations de l'utilisateur. (`code_insee_departement` incorrect sur la convention, par exemple)

## Variables d'environnement

La variable d'environnement `DEBUG_SEARCH_SCORING` permet d'avoir plus d'informations sur la manière dont est déterminée le score. Elle est utile localement et en staging, mais n'est pas adaptée à l'environnement de production car elle s'applique pour tous les utilisateurs, et affiche des logs sur la page de recherche.

`TRIGRAM_SIMILARITY_THRESHOLD` est une configuration qui permet de filtrer les résultats qui utilisent `TrigramSimilarity` qui ont un score trop faible. Si cette valeur est trop faible, la recherche affiche des résultats qui ont peu de pertinence, si elle est trop élevée elle n'autorise plus les fautes de frappes et imprécisions. La valeur par défaut a été expérimentalement placée à `0.3`.

