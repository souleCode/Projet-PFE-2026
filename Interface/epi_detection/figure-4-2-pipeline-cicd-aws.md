# Figure  : Pipeline CI/CD AWS

## Objectif

Ce document contient le prompt et les éléments nécessaires pour générer une image technique avec GPT représentant la chaîne CI/CD AWS utilisée pour déployer le backend sur EC2.

## Légende

**Caption** : Chaîne CI/CD utilisée pour l’automatisation du déploiement backend sur AWS EC2.

## Nom de fichier recommandé

`figure-pipeline-cicd-aws.png`

## Prompt GPT

```text
Génère une image technique professionnelle en français, style diagramme de pipeline CI/CD, avec fond clair, palette sobre blanc/gris clair et accents bleu/orange.

Titre du schéma : "Figure  : Pipeline CI/CD AWS"

Objectif : Illustrer la chaîne d'automatisation de déploiement backend du projet EPI Detection sur AWS EC2, depuis le code jusqu'à la production.

Le schéma doit être lisible, propre, moderne et adapté à un mémoire ou à une documentation technique.

Composants à représenter sous forme de blocs ou de zones distinctes :
1. Référentiel de code (Git)
2. AWS CodePipeline
3. AWS CodeBuild
4. AWS CodeDeploy
5. Instance EC2 de production
6. Artefacts de build
7. Environnement backend Django REST
8. Notifications / surveillance éventuelle

Flux à faire apparaître :
- Commit / push du code vers le repository
- Lancement de la pipeline CodePipeline
- Phase de build CodeBuild qui compile et prépare l'application
- Création de l'artefact de déploiement
- Transmission de l'artefact à CodeDeploy
- Déploiement de l'artefact sur l'instance EC2
- Activation de la nouvelle version backend en production

Contraintes graphiques :
- style technique, institutionnel et professionnel
- pas de rendu cartoon
- texte en français uniquement
- flèches visibles et sens du flux clair
- fond clair et blocages nets
- rendu compatible page web et document PDF

Ajouter une légende discrète en bas :
"Chaîne CI/CD utilisée pour l’automatisation du déploiement backend sur AWS EC2."
```

## Optionnel : diagramme Mermaid de base

Ce diagramme est une version textuelle simple du pipeline et peut aider à visualiser la structure avant génération d'image.

```mermaid
flowchart LR
  Git["Repository de code (Git)"] --> CodePipeline["AWS CodePipeline"]
  CodePipeline --> CodeBuild["AWS CodeBuild"]
  CodeBuild --> Artifact["Artefact de build"]
  Artifact --> CodeDeploy["AWS CodeDeploy"]
  CodeDeploy --> EC2["Instance AWS EC2"]
  EC2 -->|Déploiement backend Django| Production["Backend en production"]
```

## Utilisation

Copier ce prompt dans GPT pour générer l'image, puis enregistrer le fichier dans le dossier de documentation ou `frontend/public` selon le besoin.
