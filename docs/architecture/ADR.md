# 🧭 TACHIKOMA — ARCHITECTURE DECISION RECORDS (ADR)

Ce document regroupe **toutes les décisions d’architecture structurantes** du projet Tachikoma.

Objectifs :

* Permettre le **travail en parallèle de multiples agents IA**
* Éviter toute divergence d’architecture
* Garantir stabilité, lisibilité et évolutivité long terme

Chaque ADR correspond à **un module autonome**, avec des **interfaces contractuelles claires**.

---

## ADR-000 — Vision & Principes Fondamentaux

### Décision

Tachikoma est un **robot modulaire, pilotable par API**, orienté **sécurité, déterminisme et extensibilité**.

### Principes non négociables

* Pas de logique cachée
* Pas d’autonomie sans mode explicite
* Tout comportement doit être **observable et loggable**
* Séparation stricte :

  * contrôle
  * décision
  * perception
  * interface

### Conséquences

* Toute feature doit s’attacher à un ID de la roadmap
* Toute action physique doit pouvoir être désactivée

---

## ADR-001 — Architecture Logicielle Globale

### Décision

Architecture en **couches claires** :

```
[ Interfaces ]  →  GUI / CLI / API
[ Control ]     →  Commandes robot
[ Logic ]       →  Gaits / comportements
[ Perception ]  →  Capteurs / vision
[ Hardware ]    →  Servos / LEDs / IO
```

### Règles

* Aucune couche ne saute une autre
* L’UI ne parle jamais au hardware directement

---

## ADR-002 — Module Locomotion & Gaits

### Scope

* LOC-01 → LOC-14

### Responsabilités

* Cinématique des pattes
* Gaits (Tripod / Wave / Ripple)
* Rotation / translation / vitesse

### Interface attendue

```python
move(x: float, y: float, rotation: float, speed: int)
set_gait(name: str)
set_body(z, pitch, roll, yaw)
```

### Contraintes

* Aucun accès UI direct
* Vitesse bornée

---

## ADR-003 — Module LEDs & Feedback Visuel

### Scope

* LED-01 → LED-10

### Responsabilités

* Gestion RGB
* Animations
* États système

### Interface

```python
set_color(r,g,b)
set_mode(mode: str)
set_brightness(level: int)
```

---

## ADR-004 — Module Vision & Caméra

### Scope

* VIS-01 → VIS-12

### Responsabilités

* Stream vidéo
* Vision IA
* Tracking

### Contraintes

* Vision passive par défaut
* IA optionnelle

---

## ADR-005 — Module Capteurs & IMU

### Scope

* SEN-01 → SEN-11

### Responsabilités

* Lecture capteurs
* Normalisation
* Sécurité

### Interface

```python
get_state() -> dict
subscribe(callback)
```

---

## ADR-006 — Modes Autonomes

### Scope

* AUT-01 → AUT-07

### Décision

Les modes autonomes sont **des orchestrations**, pas des moteurs bas niveau.

### Règle

* Un mode = un état exclusif

---

## ADR-007 — API & Temps Réel

### Scope

* NET-01 → NET-06

### Décision

* REST = commande
* WebSocket = état

---

## ADR-008 — Interface GUI PyQt6

### Scope

* UI-02

### Décision

Interface **standalone**, cross-platform, PyQt6.

### Contraintes

* Aucun calcul robot dans l’UI
* Consomme uniquement l’API

---

## ADR-009 — Logs, Télémétrie & Black Box

### Scope

* DAT-01 → DAT-06

### Décision

Tout est loggé, rien n’est implicite.

---

# 🧩 DÉCOUPAGE MODULES POUR AGENTS IA

| Module            | ADR           | Agent IA |
| ----------------- | ------------- | -------- |
| Core Architecture | ADR-000 / 001 | Agent A  |
| Locomotion        | ADR-002       | Agent B  |
| LEDs              | ADR-003       | Agent C  |
| Vision            | ADR-004       | Agent D  |
| Capteurs          | ADR-005       | Agent E  |
| Autonomie         | ADR-006       | Agent F  |
| API / WS          | ADR-007       | Agent G  |
| GUI PyQt6         | ADR-008       | Agent H  |
| Logs              | ADR-009       | Agent I  |

---

📌 Chaque agent :

* ne modifie QUE son module
* respecte les interfaces
* référence les IDs roadmap
