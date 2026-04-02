# Export des conventions par département

Commande Django permettant d'exporter toutes les conventions d'un département au format Excel (`.xlsx`).

## Utilisation

```bash
python manage.py export_conventions_departement <code_departement> [options]
```

## Arguments

| Argument | Type | Obligatoire | Description |
|----------|------|-------------|-------------|
| `code_departement` | positional | Oui | Code INSEE du département (ex: `79` pour Deux-Sèvres) |
| `--output` | option | Non | Chemin du fichier de sortie. Par défaut : `conventions_<code>.xlsx` |
| `--statut` | option | Non | Filtrer par statut de convention |

## Exemples

### Export simple

```bash
python manage.py export_conventions_departement 79
```

Génère le fichier `conventions_79.xlsx` dans le répertoire courant.

### Export avec fichier de sortie personnalisé

```bash
python manage.py export_conventions_departement 79 --output /tmp/deux_sevres_conventions.xlsx
```

### Export filtré par statut

```bash
python manage.py export_conventions_departement 79 --statut "Signée"
```

## Colonnes du fichier Excel

| # | Colonne |
|---|---------|
| 1 | Numéro d'opération SIAP |
| 2 | Numéro de convention |
| 3 | Numéro d'avenant |
| 4 | Statut de la convention |
| 5 | Commune |
| 6 | Code postal |
| 7 | Code INSEE |
| 8 | Nom de l'opération |
| 9 | Instructeur |
| 10 | Type de financement |
| 11 | Nombre de logements |
| 12 | Nature de l'opération |
| 13 | Adresse |
| 14 | Raison sociale du bailleur |
| 15 | SIRET du Bailleur |
| 16 | Date de signature |
| 17 | Montant du loyer au m² |
| 18 | Livraison |
| 19 | Date de fin de conventionnement |

## Codes département courants

| Code | Département |
|------|-------------|
| 75 | Paris |
| 79 | Deux-Sèvres |
| 971 | Guadeloupe |
| 972 | Martinique |
| 973 | Guyane |
| 974 | La Réunion |
| 976 | Mayotte |

## Notes

- Aucune limite de lignes (contrairement à l'export web limité à 5 000 conventions).
- Les conventions en erreur sont ignorées et signalées dans la sortie console.
- Le tri est effectué par commune puis par numéro de convention.
