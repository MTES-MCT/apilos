# Sécuriser nos projets npm – Guide pratique pour l'équipe

## Préparer votre environnement

Avant toute installation de dépendances :

* **Ne laissez pas npm exécuter des scripts automatiquement** : certains packages peuvent contenir des scripts malveillants qui se lancent à l'installation.
  Dans votre terminal, faites :

  ```bash
  npm config set ignore-scripts true
  ```
* **Optionnel mais conseillé** : utilisez `npq`, un outil qui vérifie les packages avant installation :

  ```bash
  npm install -g npq
  npq install <nom-du-package>
  ```

> Astuce : si vous avez besoin d'installer un package avec ses scripts, vous pouvez le faire explicitement avec `--ignore-scripts false`.

---

## Installer les dépendances en toute sécurité

* **Toujours utiliser le lockfile** pour être sûr que tout le monde installe exactement les mêmes versions :

  ```bash
  npm ci
  ```
* Pour ceux qui utilisent Yarn ou pnpm :

  ```bash
  yarn install --immutable
  pnpm install --frozen-lockfile
  ```

> Cela évite les surprises et protège contre les packages malveillants qui pourraient apparaître dans des versions plus récentes.

---

## Vérifier vos dépendances et vos secrets

* Regardez bien les nouveaux packages avant de les installer.
* Ne mettez jamais de mots de passe ou clés secrètes directement dans le code ou dans `.env`.
* Si possible, utilisez un **environnement isolé** comme un conteneur Docker ou un dev container pour protéger votre machine.

---

## En résumé

* Désactiver les scripts npm par défaut
* Installer via lockfile (`npm ci`)
* Vérifier les packages et sécuriser les secrets
* Travailler dans un environnement isolé si possible

> En suivant ces étapes simples, on protège notre projet et nos machines contre des attaques via npm.