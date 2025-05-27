```{toctree}
```

# Module commentaires

## Présentation générale

APiLos permet la communication entre intructeurs et bailleurs au niveau des conventions et avenants via des commentaires.

Les commentaires concernent les conventions à instruire et en correction. Lorsqu'un instructeur instruit une convention, il peut laisser des commentaires sur des champs spécifiques du formulaire, auxquels le bailleur peut répondre. Quand la convention passe au statut en correction, le bailleur peut modifier les champs commentés.

Ainsi les commentaires servent à échanger de l'information entre instructeurs et bailleurs, mais aussi à donner la permission aux bailleurs d'éditer des champs au statut en correction.

## Implémentation des commentaires

L'application `comments` contient le coeur du code lié aux commentaires.

La table `comments_comment` contient les commentaires en base de données. Une clé étrangère pointe vers la table `conventions_convention`, de sorte qu'une convention peut avoir entre zéro et plusieurs commentaires.

Les commentaires sont représentés dans le code par le model `Comment`, parmis les différents champs, on note un statut, qui peut être `OUVERT`, `RESOLU` ou `CLOS`, un `message`qui contient le contenu du commentaire, et diverses champs permettant de savoir l'endroit exact du formulaire auquel se rattache ce commentaire.

L'application comments contient également les vues permettant de créer, mettre à jour et supprimer des commentaires.

## Lien avec le formulaire

Les commentaires sont intégrés dans les templates des formulaires de l'application.

Les différents champs génériques utilisés inclus dans leur template la ligne suivante : `{% include "common/utils/comments_field.html" %}`

Ce bout de code contient le javascript qui va instancier l'objet `CommentFactory`. Le code commence par tester sur la propriété `object_field` est présente dans le contexte, et si la convention est dans un état où l'on veut afficher les commentaires (en correction, en instruction, à signer, signée).

L'objet javascript `CommentFactory` permet de faire un apparaître une icône à côté du champ concerné. En cliquant sur l'icône on peut réaliser les différentes opérations liées aux commentaires sur ce champ (consultation, création, changement de statut).

## Permettre l'ajout de commentaire sur un nouveau champ

Quand on ajoute un champ à un formulaire de la convention, il suffit d'ajouter la propriété `object_field` pour faire apparaître l'icône des commentaires. Par exemple :

`{% include "common/form/input_text.html" with form_input=form.signataire_bloc_signature object_field="bailleur__signataire_bloc_signature__"|add:form.uuid.value %}`

Cette ligne utilise le template `input_text`, qui lui même inclut `comments_field`, qui va instancier `CommentFactory` si le statut de la convention le permet.

## Implémentation de la gestion des droits

Le code qui permet de rendre un champ éditable ou non est situé dans le template `disable_form_input.html`, inclut par défaut dans les champs du formulaires. Ce template contient la logique pour rendre le champ éditable ou non selon la présence de commentaires.

## Résumé des commentaires

Ce résumé est visible uniquement dans les status à corriger et en instruction. Il regroupe les commentaires ouverts.