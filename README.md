# MediWing

Drone quadricoptère autonome qui livre un petit kit médical (une boîte de paracétamol) et se pose grâce à un marqueur visuel ArUco.

Projet de robotique expérimentale (RO3), Polytech Nice Sophia, Rob3, 2026-2027.
Auteur : Mehdi Krifa.
Outils utilisés : Claude Code (aide au code et à la rédaction).

## Objectif

1. Voler de façon stable (Arduino Mega + MultiWii).
2. Rejoindre un point par GPS.
3. Se poser sur un marqueur ArUco (Raspberry Pi Zero 2 W + caméra).
4. Larguer le colis (servo).

## Organisation du dépôt

| Dossier | Contenu |
|---|---|
| [`comptes-rendus/`](comptes-rendus/) | Un compte rendu par séance de TP |
| [`firmware/`](firmware/) | MultiWii 2.4 configuré pour le drone (Arduino Mega) |
| [`raspberry-pi/`](raspberry-pi/) | Code Python : détection ArUco, guidage, liaison MSP |
| [`cao/`](cao/) | Pièces à imprimer : boîte du colis, loquet, support GPS |
| [`materiel/`](materiel/) | Liste des composants et schémas de câblage |
| [`docs/`](docs/) | Rapport bibliographique, documents, photos |

## Séances

| Séance | Date | Objectif | Compte rendu |
|---|---|---|---|
| S1 | 06/11/2026 | Inventaire, firmware MultiWii, pilote QMC5883L | [S1](comptes-rendus/S1-2026-11-06.md) |
| S2 | 10/11/2026 | Capteurs, GPS, radio et moteurs sur banc | |
| S3 | 17/11/2026 | Assemblage sur le châssis | |
| S4 | 24/11/2026 | Failsafe, vol stationnaire, maintien GPS | |
| S5 | 04/12/2026 | Détection du marqueur en temps réel | |
| S6 | 04/12/2026 | Atterrissage guidé | |
| S7 | 11/12/2026 | Mission complète | |
