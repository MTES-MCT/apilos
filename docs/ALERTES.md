```{toctree}
```

# Alertes SIAP

## Contexte

Historiquement, APiLos envoyait des emails aux bailleurs et instructeurs pour les informer des changements de statut sur les conventions.

Ces emails sont remplacés par les alertes SIAP.

APiLos crée et supprime des alertes dans le SIAP en appelant l'API du SIAP.

## Présentation des alertes

### Etiquette

L'étiquette de l'alerte doit faire moins de 50 caractères, sinon l'API SIAP refuse la création. Elle sera affichée à l'utilisateur dans la liste de ses alertes.

Les étiquettes listées dans le tableau ci-après contiennent le terme "convention", il est en fait dépendant de l'objet manipulé, et deviendra "avenant" dans le cas d'un avenant.

### Type

Le type d'une alerte peut-être information ou action. Les alertes information n'ont pas besoin d'être supprimées. Celles de type action doivent être supprimées quand elles deviennent caduques. A un changement de statut de la convention, on supprime toutes les alertes de type action existentes.

### Destinataire

APiLos précise au SIAP à qui est destiné une alerte concernant une convention.
Nous choisissons toujours d'envoyer les notifications aux instructeurs, côté bailleur comme côté administration.
Les deux choix de destinataires sont :
- MO : maitrise d'ouvrage, que nous appelons bailleur sur APiLos. La notification sera envoyée aux instructeurs du bailleur de la convention
- SG : service gestionnaire, que nous appelons administration sur APiLos. La notification sera envoyée aux instructeur de l'administration de la convention.

### URL de redirection

APiLos fournit aussi une url de redirection pour que l'utilisateur soit redirigé sur la convention lorsqu'il clique sur l'alerte. Les alertes renvoient au récapitulatif en général, ou en preview pour les conventions à signer.

## Liste des alertes existantes

| Etiquette | Destinataire | Déclencheur (statut de départ -> statut final) | Type (action / information) |
| ---- | ---- | ---- | ---- |
| Convention en instruction | MO | 1. Projet -> 2. Instruction requise | Information |
| Convention à instruire | SG | 1. Projet -> 2. Instruction requise | Action |
| Convention à corriger | MO | 2. Instruction requise -> 3. Corrections requises | Action |
| Convention en correction | SG | 2. Instruction requise -> 3. Corrections requises | Information |
| Convention validée à signer | MO | 2. Instruction requise -> 4. A signer | Action |
| Convention validée à signer | SG | 2. Instruction requise -> 4. A signer | Action |
| Convention en instruction | MO | 3. Corrections requises -> 2. Instruction requise | Information |
| Convention à instruire à nouveau | SG | 3. Corrections requises -> 2. Instruction requise | Action |
| Virus détecté sur un document | MO et SG | Téléversement d'un document vérollé | Information |


## Utilisation de l'API du SIAP

Le `SIAPClient` contient le code qui permet d'appeler l'API du SIAP.
Nous utilisons `create_alerte` pour la création d'alertes, et `list_convention_alertes` puis `delete_alerte` pour la suppression.

Pour le debug, `list_convention_alertes` peut-être appelée via un shell pour vérifier les alertes existantes sur une convention.
