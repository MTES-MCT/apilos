# Plan d'action - Correction des Non-Conformités RGAA 4.1.2

**Date du document :** 21 janvier 2026
**Statut :** En cours de traitement
**Objectif :** 100% de conformité aux critères RGAA 4.1.2

---

## 1. Résumé exécutif

**État actuel :** 90,38% de conformité (47 conformes / 54 non applicables / 5 non conformes)

### Critères non conformes à corriger :

| Critère | Libellé | Priorité | Pages affectées |
|---------|---------|----------|-----------------|
| **6.1** | Chaque lien est-il explicite ? | **HAUTE** | 19 pages |
| **7.1** | Compatibilité scripts / technologies d'assistance | **HAUTE** | 3 pages |
| **8.9** | Utilisation inappropriée des balises pour présentation | **MOYENNE** | 3 pages |
| **11.10** | Contrôle de saisie / aria-describedby | **MOYENNE** | 1 page |
| **13.3** | Documents bureautiques accessibles | **BASSE** | N/A |

---

## 2. Détail des corrections par critère

### 2.1 Critère 6.1 : Liens explicites (PRIORITÉ HAUTE)

**Problème :** Les liens ne possèdent pas d'intitulé explicite ou d'attribut `aria-label`.

#### Pages affectées :
- P01 - Accueil
- P02 - Accessibilité
- P03 - Mentions légales
- P04 à P19 - Pages conventions, avenants, finalisations

#### Solutions techniques :

```html
<!-- ❌ INCORRECT - Lien vague -->
<a href="/path">Plus d'infos</a>
<a href="/path">Voir</a>

<!-- ✅ CORRECT - Option 1 : Texte explicite -->
<a href="/conventions/preview">Visualiser la convention complète</a>

<!-- ✅ CORRECT - Option 2 : aria-label -->
<a href="/conventions/preview" aria-label="Visualiser la convention complète">
  <span class="icon-eye"></span>
</a>

<!-- ✅ CORRECT - Option 3 : aria-labelledby -->
<a href="/conventions/preview" aria-labelledby="link-label-123">
  <span class="icon-eye"></span>
</a>
<span id="link-label-123" class="sr-only">Visualiser la convention complète</span>
```

#### Plan de correction :

1. **Audit du code** - Identifier tous les liens avec texte vague
   ```bash
   # Rechercher les patterns problématiques :
   # - <a>Plus d'infos</a>
   # - <a>Voir</a>
   # - <a>Cliquez ici</a>
   # - <a href="..."><icon/></a> (sans texte alt)
   ```

2. **Fichiers à vérifier :**
   - `templates/` - Templates HTML
   - `conventions/templates/` - Templates conventions
   - `api/templates/` - Templates API
   - Fichiers Vue/JavaScript (si utilisation de composants frontend)

3. **Actions concrètes :**
   - [ ] Mettre à jour tous les liens "Voir", "Plus d'infos", "Cliquer" avec du texte explicite
   - [ ] Ajouter `aria-label` pour les liens iconiques uniquement
   - [ ] Vérifier les boutons stylisés en liens (utiliser `<a>` ou ajouter `role="link"`)

---

### 2.2 Critère 7.1 : Compatibilité scripts et technologies d'assistance (PRIORITÉ HAUTE)

**Problème :** Les scripts interactifs ne sont pas accessibles aux lecteurs d'écran.

#### Pages affectées :
- P01 - Accueil
- P04 - Page bailleur (étape 1/9)
- P07 - Page bailleur (Vue d'ensemble) - Bouton "mettre à jour la date"

#### Solutions techniques :

```html
<!-- ❌ INCORRECT - Bouton sans rôle approprié -->
<button onclick="updateDate()">mettre à jour la date</button>

<!-- ✅ CORRECT - Option 1 : Utiliser <a> si c'est un lien -->
<a href="javascript:updateDate()" role="button">mettre à jour la date</a>

<!-- ✅ CORRECT - Option 2 : Bouton avec aria-label -->
<button onclick="updateDate()" aria-label="Mettre à jour la date de dénonciation">
  Mettre à jour la date
</button>

<!-- ✅ CORRECT - Option 3 : Élément interactif avec ARIA -->
<div role="button" tabindex="0" onclick="updateDate()"
     onkeypress="handleKeyPress(event, updateDate)">
  Mettre à jour la date
</div>
```

#### Plan de correction :

1. **Identifier les scripts interactifs :**
   - [ ] Rechercher tous les `onclick`, `onchange`, `onfocus` dans les templates
   - [ ] Vérifier les éléments avec classe `.clickable` ou `cursor: pointer`
   - [ ] Auditer les composants JavaScript/Vue interactifs

2. **Fichiers critiques :**
   - `core/static/js/` - Scripts génériques
   - `conventions/static/js/` - Scripts conventions
   - `core/templates/` - Templates avec logique interactive

3. **Actions concrètes :**
   - [ ] Ajouter `role="button"` et `tabindex="0"` aux éléments `<div>` cliquables
   - [ ] Implémenter les événements clavier (`onkeydown`, `onkeyup`) pour `Entrée` et `Espace`
   - [ ] Ajouter `aria-label` ou `aria-describedby` pour clarifier l'action

---

### 2.3 Critère 8.9 : Balises non utilisées à fins de présentation (PRIORITÉ MOYENNE)

**Problème :** Utilisation de `<div>` pour du contenu textuel au lieu de `<p>`, `<h1>`, etc.

#### Pages affectées :
- P04, P05, P06 - Texte "Dénonciation de la convention prévue le 30 juin 2026"

#### Solutions techniques :

```html
<!-- ❌ INCORRECT - <div> pour du texte -->
<div>Dénonciation de la convention prévue le 30 juin 2026</div>

<!-- ✅ CORRECT - Utiliser les balises sémantiques -->
<p>Dénonciation de la convention prévue le 30 juin 2026</p>

<!-- ✅ CORRECT si titre - Utiliser les niveaux de titre -->
<h3>Dénonciation de la convention prévue le 30 juin 2026</h3>
```

#### Plan de correction :

1. **Localiser les divs problématiques :**
   - [ ] Rechercher `<div>Dénonciation de la convention` dans les templates
   - [ ] Vérifier les fichiers de convention

2. **Fichiers concernés :**
   - `conventions/templates/` - Templates des pages de convention
   - Particulièrement les étapes : bailleur, cadastre, récapitulatif

3. **Actions concrètes :**
   - [ ] Remplacer `<div>` par `<p>` pour le texte de dénonciation
   - [ ] Vérifier la hiérarchie des titres (h1, h2, h3)
   - [ ] Utiliser les balises structurelles : `<section>`, `<article>`, `<nav>`

---

### 2.4 Critère 11.10 : Contrôle de saisie et aria-describedby (PRIORITÉ MOYENNE)

**Problème :** L'aide à la saisie n'est pas reliée au champ de formulaire avec `aria-describedby`.

#### Pages affectées :
- P12 - Création avenant

#### Solutions techniques :

```html
<!-- ❌ INCORRECT - Aide sans connexion au champ -->
<input type="text" name="housing_count" placeholder="Nombre de logements">
<div class="help-text">L'aide à la saisie n'est pas reliée correctement</div>

<!-- ✅ CORRECT - Utiliser aria-describedby -->
<input type="text" name="housing_count" placeholder="Nombre de logements"
       aria-describedby="housing_help">
<div id="housing_help" class="help-text">
  Entrez le nombre total de logements concernés par l'avenant
</div>

<!-- ✅ CORRECT - Option avec aria-label supplémentaire -->
<label for="housing_count">Nombre de logements</label>
<input type="text" id="housing_count" name="housing_count"
       aria-label="Nombre de logements"
       aria-describedby="housing_help">
<div id="housing_help" class="help-text">
  Entrez le nombre total de logements concernés par l'avenant
</div>
```

#### Plan de correction :

1. **Identifier les champs concernés :**
   - [ ] Auditer les formulaires de la page "création avenant"
   - [ ] Vérifier tous les champs avec texte d'aide

2. **Fichiers à modifier :**
   - `conventions/forms/` - Formulaires Django
   - `conventions/templates/` - Templates de formulaires

3. **Actions concrètes :**
   - [ ] Ajouter `aria-describedby="[id]"` à tous les champs d'aide
   - [ ] S'assurer que chaque `id` est unique dans la page
   - [ ] Tester avec NVDA et JAWS

---

### 2.5 Critère 13.3 : Documents bureautiques accessibles (PRIORITÉ BASSE)

**Problème :** Les documents en téléchargement n'ont pas de version accessible.

**Note :** Critère non applicable actuellement si aucun document n'est en téléchargement.

#### Actions si applicable :

```html
<!-- ✅ Solution - Fournir une version accessible -->
<a href="/document.pdf">
  Télécharger le document
  <span class="sr-only">(PDF, 2.5 MB)</span>
</a>
<a href="/document-accessible.pdf" aria-label="Télécharger le document en version accessible">
  Version accessible
</a>
```

---

## 3. Checklist de correction par page

### Pages de convention (6.1 - Liens explicites)

- [ ] **P01** - Accueil
- [ ] **P02** - Accessibilité
- [ ] **P03** - Mentions légales
- [ ] **P04** - Bailleur étape 1/9
- [ ] **P05** - Bailleur étape 3/9 (Cadastre) + Problème 8.9
- [ ] **P06** - Bailleur Récapitulatif + Problème 8.9
- [ ] **P07** - Vue d'ensemble + Problème 7.1
- [ ] **P08** - Visualiser document
- [ ] **P09** - Finalisation étape 1/3
- [ ] **P10** - Finalisation étape 2/3
- [ ] **P11** - Finalisation étape 3/3
- [ ] **P12** - Création avenant + Problème 11.10
- [ ] **P13** - Avenant Logements
- [ ] **P14** - Convention à instruire
- [ ] **P15** - Récapitulatif commenté
- [ ] **P16** - Ajout convention étape 1
- [ ] **P17** - Ajout convention étape 2
- [ ] **P18** - Ajout convention étape 3
- [ ] **P19** - Création avenant

---

## 4. Guide d'implémentation technique

### 4.1 Structure des fichiers à modifier

```
conventions/
├── templates/
│   ├── bailleur.html          → 6.1 + 7.1 + 8.9
│   ├── cadastre.html          → 6.1 + 8.9
│   ├── recapitulatif.html     → 6.1 + 8.9
│   ├── post_action.html       → 6.1 + 7.1
│   ├── preview.html           → 6.1
│   ├── finalisation_*.html    → 6.1
│   └── avenant_*.html         → 6.1 + 11.10
├── forms/
│   └── avenant_form.py        → 11.10 (aria-describedby)
└── static/js/
    └── conventions.js         → 7.1 (accessibilité scripts)

core/templates/
├── home.html                  → 6.1 + 7.1
├── accessibility.html         → 6.1
└── cgu.html                   → 6.1
```

### 4.2 Outils de test recommandés

- **Lecteurs d'écran :** NVDA (Windows/Linux), JAWS, VoiceOver (macOS)
- **Extensions navigateur :** WCAG contrast checker, HeadingsMap, ARC Toolkit, PAC
- **Validation HTML :** W3C Validator
- **Audit automatisé :** Axe DevTools, Lighthouse

### 4.3 Workflow de correction

1. **Phase 1 - Analyse détaillée**
   - [ ] Générer une liste complète des liens non explicites
   - [ ] Localiser tous les scripts non accessibles
   - [ ] Documenter les impacts utilisateur

2. **Phase 2 - Correction**
   - [ ] Créer une branche de développement : `feat/accessibility-rgaa-compliance`
   - [ ] Corriger critère par critère
   - [ ] Tester avec les lecteurs d'écran identifiés

3. **Phase 3 - Validation**
   - [ ] Audit manuel sur les 19 pages testées
   - [ ] Tests automatisés (Axe, Lighthouse)
   - [ ] Validation RGAA 4.1.2

4. **Phase 4 - Déploiement**
   - [ ] Merge sur branche principale
   - [ ] Audit externe de vérification
   - [ ] Mise à jour de la déclaration d'accessibilité

---

## 5. Ressources externes

- **RGAA 4.1.2 :** https://accessibilite.numerique.gouv.fr/
- **WCAG 2.1 Level AA :** https://www.w3.org/WAI/WCAG21/quickref/
- **Opquast Checklist :** https://checklists.opquast.com/
- **MDN - Accessibilité Web :** https://developer.mozilla.org/fr/docs/Web/Accessibility

---

## 6. Timeline estimée

| Phase | Durée estimée | Critères | Statut |
|-------|---------------|----------|--------|
| Analyse détaillée | 2-3 jours | 6.1, 7.1 | À faire |
| Correction 6.1 | 3-4 jours | Liens explicites | À faire |
| Correction 7.1 | 2-3 jours | Scripts accessibles | À faire |
| Correction 8.9 | 1-2 jours | Balises sémantiques | À faire |
| Correction 11.10 | 1 jour | aria-describedby | À faire |
| Tests & validation | 2-3 jours | Tous | À faire |
| **Total** | **11-16 jours** | | |

---

## 7. Notes de suivi

**Mise à jour :** 21 janvier 2026

### Prochaines étapes :
1. Assigner les tâches par critère/page
2. Planifier les ressources (dev, testeur accessibilité)
3. Mettre en place les outils de test automatisé
4. Créer des tests unitaires pour les composants accessibles

---

**Document maintenu par :** L'équipe produit APIlos
**Prochaine revue :** À définir après audit de conformité complet
