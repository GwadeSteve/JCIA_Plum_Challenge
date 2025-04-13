<h1 align="center">
  <br>
  <span style="font-size: 2.5em; font-weight: bold; color:rgb(219, 197, 255);">Plum</span><span style="font-size: 2.5em; font-weight: bold; color:rgb(131, 148, 245);">Vision</span>
  <br>
</h1>

<h4 align="center">Un prototype intelligent pour le tri de prunes africaines, développé pour le JCIA Hackathon 2025.</h4>

<p align="center">
  <a href="https://github.com/GwadeSteve/JCIA_Plum_Challenge">
    <img src="https://img.shields.io/badge/Team-PlumVision-blue.svg"
         alt="Team PlumVision">
  </a>
  <a href="https://docs.google.com/document/d/1kwnXUpNghQ26GdF27YRTiQVNn4JaiepmSHreTG065LM/edit?pli=1&tab=t.0">
    <img src="https://img.shields.io/badge/Hackathon-JCIA%202025-brightgreen.svg"
         alt="JCIA Hackathon 2025">
  </a>
</p>

<p align="center">
  <a href="#fonctionnalites-cles">Fonctionnalités Clés</a> •
  <a href="#demonstration">Démonstration</a> •
  <a href="#technologies-utilisees">Technologies Utilisées</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#comment-demarrer">Comment Démarrer</a> •
  <a href="#equipe">Équipe</a>
</p>

---

## Fonctionnalités Clés

* Analyse en temps réel du flux vidéo d'une caméra connectée pour classifier les prunes.
* Classification des prunes en six catégories de qualité : Bonne qualité, non mûre, tachetée, fissurée, meurtrie, pourrie.
* Interface utilisateur web simple pour visualiser le flux de la caméra, les prédictions et les statistiques.
* Suivi en temps réel du nombre total de prunes traitées et de leur répartition par catégorie (Statistiques de Session).
* Génération automatique de commentaires sur la qualité globale du tri via l'API Gemini (Commentaires IA).
* Possibilité d'uploader une image pour une prédiction unique.

---

## Démonstration

<p align="center">
  <img src="./plumvision-demo.gif" alt="Démonstration de PlumVision">
</p>

---

## Technologies Utilisées

* **Modèles de Deep Learning :** PyTorch
* **Backend :** FastAPI
* **Frontend :** ReactJS
* **IA Générative :** Gemini API
* **Base de Données (Prototype) :** SQLite

---

## ⚙️ Architecture

<p align="center">
  <img src="./Image.png" width="600" alt="Architecture du Système">
</p>

---

## Comment Démarrer (Prototype - Démonstration)

1. Lancez l'application web.
2. Dans la section de prédiction, démarrez la session de scan en temps réel. Assurez-vous que la caméra est accessible.
3. Le système affichera en direct le flux vidéo, les classifications des prunes détectées et les statistiques de la session.
4. Vous pouvez arrêter la session à tout moment.
5. La section Dashboard affichera un récapitulatif des statistiques de la session après son arrêt.

---

## Équipe

PlumVision

---

## 📄 Licence

[MIT](LICENSE)

---

> Projet développé pour le JCIA Hackathon 2025.