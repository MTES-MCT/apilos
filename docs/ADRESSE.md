# Champ adresse

Ce champ est particulier parce qu'il est défini à deux endroits de la base de données.

## Champ adresse du programme

A la création du modèle de données d'APiLos, le champ adresse a été rattaché à l'objet programme. En effet dans un cas classique, le programme correspond à une seule adresse postale (par exemple un seul batiment, ou plusieurs batiments situés à la même adresse).

C'est pourquoi le champ adresse est défini sur le modèle Programme. Nous remplissons ce champ à partir de l'adresse de l'opération récupérée sur le SIAP, via la fonction `get_or_create_programme`.

## Champ adresse d'une convention

Durant les premières années de mise en service d'APiLos, il a été remonté plusieurs fois au support ce que les utilisateurs considéraient comme un bug : changer l'adresse d'une convention changeait aussi l'adresse des autres conventions du programme.

Ce comportement s'explique parce que le champ adresse est rattaché à l'objet Programme. Le besoin des utilisateurs de changer l'adresse d'une convention spécifique était justifié : il existe des cas où un même programme correspond à plusieurs adresses postales, comme par exemple des batiments à un angle de rues, qui font l'objet de deux types de financements distincts.

### Initialisation du champ

Pour cette raison, nous avons ajouté un champ adresse sur le modèle Convention. Il n'est pas rempli au moment de la création de la convention depuis le SIAP, il possède alors la valeur `NULL`.

### Utilisation dans l'étape programme

Dans le formulaire de convention, lors de l'étape programme, l'utilisateur a la possilité de modifier l'adresse de la convention. Ce champ est initialisé à partir de l'adresse du programme.

La logique de remplissage se trouve dans `ConventionProgrammeService.get`, le champ adresse y prend la valeur `self.convention.adresse or programme.adresse`. Lors du premier remplissage, l'adresse de la convention est vide donc c'est la valeur de l'adresse du programme qui est affichée. Ensuite cette valeur est enregristrée dans le champ adresse de la convention, via `_save_convention_adresse`. Elle sera ensuite utilisée pour initialiser le champ adresse du formulaire si l'utilisateur revient l'éditer.

Ce choix de deux champs nous a permis de rendre modifiable le champ adresse au niveau de la convention, sans necessiter de migrations de données au moment de l'implémentation.

## Perspectives

On pourrait envisager la supression du champ au niveau du programme, ce qui nécessiterait une migration de la valeur du champ adresse au niveau des conventions où il se trouve vide (conventions déjà complétées avant cette feature, nouvelles conventions pas encore complétées). Cela permettrait une simplification du code au niveau de la gestion du champ adresse.
