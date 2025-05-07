```{toctree}
```

# Présentation générale

Une convention APL, une fois signée par les deux parties, peut-être amenée à évoluer durant son cycle de vie pour des raisons variées (rachat d'un bailleur, modification de l'adresse suite au changement de nom d'une rue...).

La modification des conventions signées passent par des avenants.

# Modèle de données

## Lien entre avenants et conventions

En base de données, les avenants sont stockés dans la même table que les conventions : conventions_convention.

Une entrée de la table conventions_convention est donc soit une convention, soit un avenant.

-> Une entrée qui possède un parent_id à `NULL` est une convention
-> Une entrée qui possède une valeur dans `parent_id`  est un avenant

Le parent_id représente la convention d'origine de l'avenant.

Exemple : Une convention a pour id (pk) 118. Son parent_id est NULL, comme pour toutes les conventions.
Elle possède un premier avenant ayant pour id 223 et pour parent_id 118 et un second avenant ayant pour id 264 et parent_id 118.

Attention : il n'est pas exlu qu'il existe en base de données des avenants dont le parent_id ne pointe pas vers la convention d'origine, mais vers le précédent avenant à cette convention, suite à des modifications manuelles via le back office.

## Types d'avenants

Les avenants peuvent posséder un ou plusieurs types d'avenants, permettant de savoir sur quels sections portent les modifications. A la création d'un avenant, il ne possède aucun type d'avenant tant qu'aucun bloc n'a été coché dans la vue récapitulatif.

Les différents types d'avenants sont définis dans la table `conventions_avenanttype`, et modifiables depuis le back-office (en cas d'ajout de nouveaux types d'avenants). La table conventions_avenanttype et la table `conventions_convention` sont liées par une relation many to many via la table de liaison `conventions_convention_avenant_types`.

# Création d'avenants

Lors de la création d'un avenant, le nouvel avenant est créé comme une copie des données du dernier avenant de la convention (ou de la convention elle-même si elle n'a pas encore d'avenant).

Cette copie est effectuée par la méthode `clone` du modèle `Convention`.

# Gestion des types d'avenant

Lorsqu'on coche un bloc dans la vue récapitulatif d'un avenant, cela ajoute l'avenant_type correspondant à l'avenant, et nous redirige vers le formulaire pour éditer les champs liés à ce type.

Lorsqu'on décoche un bloc, cela supprime l'avenant_type de l'avenant, et redonne également aux champs liés à cet avenant_type leur valeur d'origine, celles du dernier avenant (ou de la convention si celle-ci n'avait pas encore d'avenant).

Pour remettre les champs à leur valeur d'origine, un signal est reçu lors d'un changement de la relation m2m par le handler `post_save_reset_avenant_fields_after_block_delete`.

Ce handler vérifie s'il s'agit d'une suppression d'avenant_type, et si c'est le cas, redonne aux champs liés à l'avenant_type les valeurs d'origine, en s'appuyant sur le mapping `AVENANT_TYPE_FIELDS_MAPPING`.