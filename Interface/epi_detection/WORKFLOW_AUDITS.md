# Workflow Audits

## Rôle de l'audit

Dans ce projet, une alerte signale une non-conformité détectée par l'IA.

Un audit sert à transformer cette alerte en dossier de suivi opérationnel.

L'idée métier est la suivante :

- l'alerte répond à la question `qu'est-ce qui se passe maintenant ?`
- l'audit répond à la question `qu'est-ce qu'on fait de ce problème, qui le traite, et avec quelle traçabilité ?`

Un audit permet donc de :

- formaliser une investigation
- suivre des actions correctives
- attacher des captures et des notes
- garder un statut de traitement
- produire un export PDF ou CSV

## Workflow métier recommandé

### 1. Détection

Le système détecte une non-conformité EPI depuis une caméra.

Résultat :

- création d'un log de détection
- création éventuelle d'une alerte

### 2. Qualification de l'alerte

L'utilisateur consulte l'alerte et décide si elle nécessite seulement un traitement simple ou une investigation complète.

Cas simples :

- incident mineur et isolé
- faux positif
- correction immédiate sans besoin de suivi

Cas nécessitant un audit :

- incident récurrent
- criticité élevée
- besoin de preuve de traitement
- besoin d'analyse cause racine
- besoin de suivi HSE / supervision / inspection

### 3. Ouverture de l'audit

Depuis l'alerte, un utilisateur ouvre un audit.

Le formulaire crée un audit avec :

- un titre
- la caméra concernée
- l'alerte source
- des notes initiales

L'audit passe ensuite dans le cycle :

- `ouvert`
- `en_cours`
- `clos`

### 4. Suivi de l'audit

Pendant l'audit, on peut :

- documenter le contexte
- ajouter des captures
- préciser les constats
- suivre l'état du traitement

### 5. Clôture

L'audit est clôturé quand :

- la situation a été traitée
- l'action corrective est connue ou réalisée
- le dossier contient assez de contexte pour être archivé ou exporté

## Règles métier pour décider d'ouvrir un audit

Toutes les alertes ne doivent pas devenir des audits.

L'ouverture d'un audit est pertinente dans les cas suivants.

### Criticité élevée

Ouvrir un audit si l'alerte est :

- `elevee`

Raison :

- il faut une trace formelle du traitement

### Récidive sur une même caméra ou une même zone

Ouvrir un audit si plusieurs alertes similaires reviennent sur :

- la même caméra
- la même zone
- la même règle HSE

Raison :

- cela signale un problème structurel, pas seulement un incident ponctuel

### Incidents répétés sur un EPI critique

Ouvrir un audit si l'EPI manquant concerne régulièrement :

- casque
- gilet
- lunettes
- protection auditive

Raison :

- cela peut révéler un manque de discipline, d'équipement, d'affichage ou de contrôle terrain

### Besoin de preuve ou d'escalade HSE

Ouvrir un audit si l'incident doit être :

- analysé par un superviseur
- partagé à un responsable HSE
- archivé comme preuve de traitement
- exporté en rapport PDF

### Incident non résolu rapidement

Ouvrir un audit si une alerte reste :

- `nouveau` trop longtemps
- `en_cours` sans clôture claire

Raison :

- il faut sortir du traitement temps réel et passer en suivi structuré

## Règles simples à appliquer dans l'interface

Pour une première version produit, on peut appliquer cette logique :

### Ouvrir automatiquement un audit suggéré si

- criticité = `elevee`
- ou même caméra avec au moins 3 alertes récentes
- ou même EPI manquant répété plusieurs fois dans la journée

### Laisser l'ouverture manuelle sinon

- l'utilisateur garde la décision d'ouvrir ou non un audit

## Implémentation actuelle dans le projet

Le flux minimal existe déjà dans l'interface.

Depuis la page Alertes :

- bouton `Ouvrir audit`
- modal simple avec titre et notes
- création via `POST /api/audits/`

Le backend prend déjà en charge :

- création d'audit
- détail d'audit
- mise à jour du statut
- ajout de captures
- export PDF et CSV

## Prochaines améliorations recommandées

### UI

- ajouter une page détail audit
- afficher l'audit lié directement depuis la liste des alertes
- empêcher l'ouverture de doublons pour une même alerte si besoin

### Règles automatiques

- suggérer automatiquement l'ouverture d'un audit pour certaines alertes
- calculer un score de priorité d'audit

### Reporting

- nombre d'audits ouverts par période
- délai moyen de clôture
- taux d'audits issus d'alertes critiques
- répartition des audits par caméra, zone et règle HSE