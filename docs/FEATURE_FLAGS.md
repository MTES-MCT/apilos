```{toctree}
```

# Utilisation des feature flags par APiLos

Les feature flags permettent d'activer ou de désactiver des fonctionnalités du projet directement en production sans avoir à faire un nouveau déploiement.

## Cas d'utilisation

### Intégration progressive

Les feature flags permettent des mises en production régulières lors du développement d'une grosse fonctionnalité, sans attendre que celle-ci soit terminée.

Cela permet une intégration du code progressive et évite les mises en production risquées.

### Fonctionnalité risquée

Certaines nouvelles fonctionalités sont difficiles à tester hors conditions réelles, par exemple la modification de requêtes SQL pouvant entraîner des problèmes de performance.

Un feature flag permet de diminuer le risque d'interruption de service, grâce au contrôle du moment exact d'activation et la possibilité d'une désactivation immédiate.

### Beta testing

Un flag peut-être activé pour un sous-ensemble des utilisateurs, permettant de tester des fonctionnalités avant de les ouvrir à l'ensemble des utilisateurs.

## Implémentation

Nous utilisons la librairie `django-waffle` pour l'implémentation des feature flags. Elle propose des switchs activables pour l'ensemble du site via l'admin, ou des flags activables pour des utilisateurs en particulier.

https://waffle.readthedocs.io/en/stable

## Cycle de vie des flags

Nous n'avons pas de protocole en place pour supprimer un feature flag. Il peut être intéressant de créer un ticket de suppression du flag dans le backlog à chaque fois qu'on crée un nouveau flag, pour anticiper sa suppression.

Un flag n'a pas vocation à rester dans le code après son activation, il peut être supprimé quelques jours ou semaines après.

## Feature flags du projet

| Nom | Type | |
|---|---|---|
| SWITCH_VISIBILITY_AVENANT_BAILLEUR | Switch | Détermine la visiblité des conventions en fonction des avenants bailleur |
| FLAG_ADD_CONVENTION | Flag | Active l'ajout simplifié de convention |
| SWITCH_SIAP_ALERTS_ON | Switch | Active la création d'alertes lors des changements de statuts de convention |
| SWITCH_TRANSACTIONAL_EMAILS_OFF | Switch | Désactive l'envoi d'emails lors des changements de statuts de convention |
