```{toctree}
```

# Gestion des étapes des formulaires

## Principe

Nous découpons les formulaires en étapes pour simplifier leur remplissage par les utilisateurs.

Nous appelons "stepper" le bloc situé en haut des formulaires qui permet d'en suivre les étapes.

## Petits formulaires

Pour les formulaires de finalisation, publication et création de convention depuis une opération, nous utilisons la classe `Stepper`.

Chaque étape de ces formulaires ont une url dédiée, qui pointe sur une vue propre à chaque étape. Chaque vue définie une step_number qui caréctérise sa position parmis les autres étapes, et hérite d'une vue commune à tout le formulaire qui contient la logique du stepper.

La vue de base (par exemple `FinalisationBase`) intialise un `Stepper` à partir du nom des différentes étapes.

## Formulaire de convention

Le formulaire principal du site utilise la classe `ConventionFormStep` plutôt que le `Stepper`, parce qu'il contient de la logique additionnelle.



