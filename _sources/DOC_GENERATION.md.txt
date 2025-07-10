```{toctree}
```

# Génération de docx et pdf

## Librairie docxtpl

Cette librairie utilise jinja2 et python-docx pour permettre de réaliser du templating jinja à l'intérieur de fichiers docx.

`https://docxtpl.readthedocs.io/en/latest/`

Nous utilisons cette librairie pour générer les différents documents.

## Templates docx

Le dossier `documents` contient des fichiers docx utilisés pour générer les documents de conventions, d'avenants et la fiche caf.

Le contenu suit la syntaxe de templating Jinja, permettant aux documents d'être complétés avec les informations entrés sur APiLos.

Ce tableau liste les templates existants.

| Nom                             | Type       | Nature               | Bailleur |
|---------------------------------|------------|----------------------|----------|
| Avenant-template                | Avenant    | Logements ordinaires | x        |
| FicheCAF-template               | Fiche CAF  | x                    | x        |
| Foyer-template                  | Convention | Foyers               | x        |
| FoyerResidence-Avenant-template | Avenant    | Foyers et résidences | x        |
| HLM-template                    | Convention | Logements ordinaires | HLM      |
| Residence-template              | Convention | Residences           | x        |
| SEM-template                    | Convention | Logements ordinaires | SEM      |
| Type1-template                  | Convention | Logements ordinaires | Type 1   |
| Type2-template                  | Convention | Logements ordinaires | Type 2   |

Ce tableau permet de retrouver quels documents sont utilisés pour quelles conventions. C'est utile pour prendre en compte les modifications apportées aux formulaires APILos dans les templates de documents.

Par exemple un nouveau champ est ajouté aux conventions logements ordinaires sur le site APiLos. Il faut alors mettre à jour les documents relatifs aux logements ordinaires pour y ajouter ce champ à l'endroit convenu avec le métier. Cela implique pour le cas des logements ordinaires la modification de 5 templates.

## Génération de docx

Le code responsable de la génération des documents est situé dans `conventions/services/convention_generator.py`

La fonction `generate_convention_doc` génère le document de convention ou d'avenant. Elle construit le contexte qui va être utilisé pour générer le document à partir du templating.

## Conversion en pdf

Toujours dans le fichier `conventions/services/convention_generator.py`, la fonction `generate_pdf` a pour rôle de convertir un fichier docx en pdf, en utilisant libreoffice.

La variable d'environnement `LIBREOFFICE_EXEC` contient le chemin vers l'executable de libreoffice.