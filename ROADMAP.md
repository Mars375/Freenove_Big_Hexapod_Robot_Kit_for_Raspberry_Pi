# 🤖 TACHIKOMA — ROADMAP OFFICIELLE

Ce document est la **source unique de vérité** pour le développement du robot **Tachikoma**.
Il décrit **toutes les fonctionnalités**, leur **statut**, leur **priorité**, et leur **ordonnancement**.

Toute implémentation, discussion technique ou décision d’architecture DOIT se rattacher à cette roadmap.

---

## 🔖 Légende

* ✅ Implémenté et fonctionnel
* ⚠️ Implémenté mais bugué / instable
* 🔲 Non implémenté

---

## 🚶 LOCOMOTION

| ID     | Fonction                       | Statut |
| ------ | ------------------------------ | ------ |
| LOC-01 | Avancer (vitesse variable)     | ✅      |
| LOC-02 | Reculer                        | ✅      |
| LOC-03 | Déplacement latéral droit      | ✅      |
| LOC-04 | Déplacement latéral gauche     | ✅      |
| LOC-05 | Rotation droite (pivot)        | ⚠️     |
| LOC-06 | Rotation gauche (pivot)        | ⚠️     |
| LOC-07 | Réglage vitesse (2–10)         | ⚠️     |
| LOC-08 | Altitude corps (Z)             | 🔲     |
| LOC-09 | Balance Pitch / Roll / Yaw     | 🔲     |
| LOC-10 | Marche crabe / diagonale       | 🔲     |
| LOC-11 | Gaits (Tripod / Wave / Ripple) | 🔲     |
| LOC-12 | Danse / séquences              | 🔲     |
| LOC-13 | Auto-stabilisation IMU         | 🔲     |
| LOC-14 | Évitement obstacles            | 🔲     |

---

## 🎨 LEDs

| ID     | Fonction                | Statut |
| ------ | ----------------------- | ------ |
| LED-01 | Couleur fixe RGB        | ✅      |
| LED-02 | Extinction              | ✅      |
| LED-03 | Arc-en-ciel animé       | ⚠️     |
| LED-04 | Luminosité              | 🔲     |
| LED-05 | Clignotement            | 🔲     |
| LED-06 | Respiration             | 🔲     |
| LED-07 | Vague                   | 🔲     |
| LED-08 | Indicateur batterie     | 🔲     |
| LED-09 | Indicateur état système | 🔲     |
| LED-10 | Synchronisation musique | 🔲     |

---

## 🎥 VISION & CAMÉRA

| ID     | Fonction             | Statut |
| ------ | -------------------- | ------ |
| VIS-01 | Stream vidéo live    | 🔲     |
| VIS-02 | Pan / Tilt caméra    | 🔲     |
| VIS-03 | Face detection       | 🔲     |
| VIS-04 | Face tracking        | 🔲     |
| VIS-05 | Object detection     | 🔲     |
| VIS-06 | Line following       | 🔲     |
| VIS-07 | QR Code              | 🔲     |
| VIS-08 | Détection de couleur | 🔲     |
| VIS-09 | Capture photo        | 🔲     |
| VIS-10 | Enregistrement vidéo | 🔲     |
| VIS-11 | Vision nocturne      | 🔲     |
| VIS-12 | Overlay AR           | 🔲     |

---

## 🔊 AUDIO

| ID     | Fonction              | Statut |
| ------ | --------------------- | ------ |
| AUD-01 | Beep simple           | ✅      |
| AUD-02 | Tonalités             | 🔲     |
| AUD-03 | Mélodies              | 🔲     |
| AUD-04 | Alarmes               | 🔲     |
| AUD-05 | Effets sonores        | 🔲     |
| AUD-06 | Text-to-Speech        | 🔲     |
| AUD-07 | Reconnaissance vocale | 🔲     |

---

## 📡 CAPTEURS

| ID     | Fonction               | Statut |
| ------ | ---------------------- | ------ |
| SEN-01 | Batterie (voltage)     | ✅      |
| SEN-02 | IMU (Pitch/Roll/Yaw)   | ✅      |
| SEN-03 | Sonar distance         | ⚠️     |
| SEN-04 | Gyroscope              | 🔲     |
| SEN-05 | Accéléromètre          | 🔲     |
| SEN-06 | Magnétomètre           | 🔲     |
| SEN-07 | Température            | 🔲     |
| SEN-08 | Pression atmosphérique | 🔲     |
| SEN-09 | Luminosité             | 🔲     |
| SEN-10 | Courant moteurs        | 🔲     |
| SEN-11 | Feedback servos        | 🔲     |

---

## 🎮 CALIBRATION & SETUP

| ID     | Fonction                   | Statut |
| ------ | -------------------------- | ------ |
| CAL-01 | Calibration manuelle servo | ✅      |
| CAL-02 | Sauvegarde calibration     | ✅      |
| CAL-03 | Auto-calibration           | 🔲     |
| CAL-04 | Relax mode (servos off)    | 🔲     |
| CAL-05 | Reset pose neutre          | 🔲     |
| CAL-06 | Test servos                | 🔲     |
| CAL-07 | Diagnostic complet         | 🔲     |
| CAL-08 | Limites sécurité           | 🔲     |
| CAL-09 | Trim fin                   | 🔲     |

---

## 🤖 MODES AUTONOMES

| ID     | Fonction            | Statut |
| ------ | ------------------- | ------ |
| AUT-01 | Patrouille          | 🔲     |
| AUT-02 | Exploration         | 🔲     |
| AUT-03 | Retour base         | 🔲     |
| AUT-04 | Suivi personne      | 🔲     |
| AUT-05 | Mode gardien        | 🔲     |
| AUT-06 | Mode jeu            | 🔲     |
| AUT-07 | Sommeil basse conso | 🔲     |

---

## 💾 DONNÉES & LOGS

| ID     | Fonction                   | Statut |
| ------ | -------------------------- | ------ |
| DAT-01 | Enregistrement trajectoire | 🔲     |
| DAT-02 | Replay trajectoire         | 🔲     |
| DAT-03 | Télémétrie temps réel      | 🔲     |
| DAT-04 | Logs JSON structurés       | 🔲     |
| DAT-05 | Statistiques               | 🔲     |
| DAT-06 | Black box                  | 🔲     |

---

## 🌐 CONNECTIVITÉ

| ID     | Fonction             | Statut |
| ------ | -------------------- | ------ |
| NET-01 | API REST             | ✅      |
| NET-02 | WebSocket temps réel | ⚠️     |
| NET-03 | MQTT                 | 🔲     |
| NET-04 | Bluetooth            | 🔲     |
| NET-05 | WiFi AP              | 🔲     |
| NET-06 | Cloud sync           | 🔲     |

---

## 🖥️ INTERFACES

| ID    | Fonction          | Statut |
| ----- | ----------------- | ------ |
| UI-01 | CLI terminal      | ✅      |
| UI-02 | GUI Desktop PyQt6 | 🔲     |
| UI-03 | Web Dashboard     | 🔲     |
| UI-04 | Mobile App        | 🔲     |
| UI-05 | VR / AR Control   | 🔲     |
| UI-06 | Gamepad support   | 🔲     |

---

## 📅 PHASES

### PHASE 1 — FONDATIONS

* LOC-05 / LOC-06 / LOC-07
* LED-03
* SEN-03
* NET-02
* UI-02

### PHASE 2 — CORE

* LOC-08 / LOC-09
* CAL-04
* VIS-01 / VIS-02
* LED-04 → LED-09

### PHASE 3 — INTELLIGENCE

* VIS-03 → VIS-06
* LOC-13 / LOC-14
* AUT-01 → AUT-04

### PHASE 4 — AVANCÉ

* SLAM
* Multi-robots
* Voice control
* Cloud
* Mobile

---

📌 **Toute modification de ce document doit être volontaire, tracée et justifiée.**

