# 🧠 PlumVision – JCIA Hackathon 2025

## 🌾 Nom de l'équipe : **AgriNova AI**

---

## 🎯 Objectif

Développer une solution intelligente de **tri automatique de prunes africaines** via une chaîne de traitement temps réel, classifiant chaque prune dans l'une des **6 catégories** :

- ✅ Bonne qualité
- 🟡 Non mûre
- 🔴 Tachetée
- ⚫ Fissurée
- 💢 Meurtrie
- 💀 Pourrie

Fonctionnalités principales :
- 📷 Classification en **temps réel** via caméra fixe (ex. au-dessus d’un tapis roulant)
- 🌐 Interface web de monitoring et prédiction (upload / webcam)
- 🧠 Prédictions par **modèles multi-étapes** (superclasse + défauts)
- ✨ Génération de **commentaires automatiques** via Gemini API
- 📊 Tableau de bord avec statistiques de tri par session

---

## 🧠 Stack Technique

| Composant         | Outils / Langages                                      |
|-------------------|--------------------------------------------------------|
| Modèles ML        | PyTorch, YOLOv8-cls, EfficientNetB0, MobileNetV2       |
| Backend API       | **FastAPI** + Uvicorn (temps réel, rapide, asynchrone) |
| Frontend          | **React + TailwindCSS + Axios + Chart.js**            |
| Temps réel        | **SSE (Server-Sent Events)** / WebSockets (optionnel)  |
| Déploiement       | Docker, Gunicorn, Nginx (si besoin)                    |
| IA Générative     | Gemini API (Google AI Studio)                          |
| Entraînement      | Jupyter Notebooks + PyTorch                            |
| Stockage/DB       | SQLite (prototype) ou PostgreSQL (production)          |
| Dataset           | African Plums Dataset (Kaggle)                         |

---

## 🧹 Architecture du Système

```plaintext
                             CAMÉRA / STREAMING
                                (temps réel)
                                     │
                             [ Capture par Frontend ]
                                     │
                                     ▼
📈 Interface Web ➔ API FastAPI ➔ Modèles PyTorch (superclasse / défauts)
         └️ SSE temps réel ← Base de données (sessions)
                                 └️ Gemini (commentaires IA)
```

---

## 📲 Cas d’usage typique (Entreprise)

> 🎥 **Sur le terrain :** Une entreprise installe le système au-dessus d’un tapis roulant. À l’ouverture du logiciel :
>
> 1. 📡 Une **session de tri est lancée**
> 2. 📷 Les images des prunes sont **capturées en direct**
> 3. 🧠 Le backend **classifie** chaque prune (via modèles)
> 4. 🚦 Un signal est envoyé à un système **de redirection physique**
> 5. 📊 Une interface affiche en temps réel :
>    - Nombre total de prunes triées
>    - Répartition par catégorie
>    - Taux de qualité globale
>    - Historique de tri
> 6. 📟 À la fin, un **rapport automatique** est généré.

---

## 📁 Structure du Projet

```bash

├── JCIA_PLUM_DATA_CHALLENGE/
│   ├── .gitignore
│   ├── Plan.md
│   ├── prompt.txt
│   ├── african_plums_dataset/
│   │   ├── README.md
│   │   ├── data.yaml
│   │   ├── organized_plums_data_new.csv
│   │   ├── processed_csv.csv
│   │   ├── african_plums/
│   │   │   ├── bruised/
│   │   │   ├── cracked/
│   │   │   ├── rotten/
│   │   │   ├── spotted/
│   │   │   ├── unaffected/
│   │   │   ├── unripe/
│   │   ├── cleaned_data/
│   │   │   ├── class_weights.json
│   │   │   ├── test.cache
│   │   │   ├── train.cache
│   │   │   ├── val.cache
│   │   │   ├── test/
│   │   │   │   ├── bruised/
│   │   │   │   ├── cracked/
│   │   │   │   ├── rotten/
│   │   │   │   ├── spotted/
│   │   │   │   ├── unaffected/
│   │   │   │   ├── unripe/
│   │   │   ├── train/
│   │   │   │   ├── bruised/
│   │   │   │   ├── cracked/
│   │   │   │   ├── rotten/
│   │   │   │   ├── spotted/
│   │   │   │   ├── unaffected/
│   │   │   │   ├── unripe/
│   │   │   ├── val/
│   │   │   │   ├── bruised/
│   │   │   │   ├── cracked/
│   │   │   │   ├── rotten/
│   │   │   │   ├── spotted/
│   │   │   │   ├── unaffected/
│   │   │   │   ├── unripe/
│   │   ├── defect_data/
│   │   │   ├── class_weights.json
│   │   │   ├── test.cache
│   │   │   ├── train.cache
│   │   │   ├── val.cache
│   │   │   ├── test/
│   │   │   │   ├── bruised/
│   │   │   │   ├── cracked/
│   │   │   │   ├── rotten/
│   │   │   │   ├── spotted/
│   │   │   ├── train/
│   │   │   │   ├── bruised/
│   │   │   │   ├── cracked/
│   │   │   │   ├── rotten/
│   │   │   │   ├── spotted/
│   │   │   ├── val/
│   │   │   │   ├── bruised/
│   │   │   │   ├── cracked/
│   │   │   │   ├── rotten/
│   │   │   │   ├── spotted/
│   │   ├── superclass_data/
│   │   │   ├── class_weights.json
│   │   │   ├── test.cache
│   │   │   ├── train.cache
│   │   │   ├── val.cache
│   │   │   ├── test/
│   │   │   │   ├── defective/
│   │   │   │   ├── unaffected/
│   │   │   │   ├── unripe/
│   │   │   ├── train/
│   │   │   │   ├── defective/
│   │   │   │   ├── unaffected/
│   │   │   │   ├── unripe/
│   │   │   ├── val/
│   │   │   │   ├── defective/
│   │   │   │   ├── unaffected/
│   │   │   │   ├── unripe/
│   ├── Models/
│   │   ├── Trained/
│   │   │   ├── mobilenet/
│   │   │   ├── yolo/
│   │   │   │   ├── yolov11n/
│   │   │   │   ├── yolov11s/
│   │   │   │   ├── yolov8n/
│   │   │   │   ├── yolov8s/
│   │   ├── Trained-DefectClass/
│   │   │   ├── yolo/
│   │   │   │   ├── yolov11n/
│   │   │   │   ├── yolov11s/
│   │   │   │   ├── yolov8n/
│   │   │   │   ├── yolov8s/
│   │   ├── Trained-Superclass/
│   │   │   ├── yolo/
│   │   │   │   ├── yolov11n/
│   │   │   │   ├── yolov11s/
│   │   │   │   ├── yolov8n/
│   │   │   │   ├── yolov8s/
│   │   ├── Untrained/
│   │   │   ├── yolov11/
│   │   │   │   ├── yolo11n-cls.pt
│   │   │   │   ├── yolo11s-cls.pt
│   │   │   ├── yolov8/
│   │   │   │   ├── yolov8n-cls.pt
│   │   │   │   ├── yolov8s-cls.pt
│   ├── Notebooks/
│   │   ├── DefectClassTraining.ipynb
│   │   ├── DefectClassesSplit.ipynb
│   │   ├── Exploration.ipynb
│   │   ├── SuperClassSplit.ipynb
│   │   ├── SuperClassTraining.ipynb
│   │   ├── YoloTraining.ipynb
```

---

## ⚙️ Backend – Fonctionnement

- **/predict** : reçoit une image, retourne la prédiction
- **/stream** : envoie les événements temps réel (SSE)
- **/metrics** : retourne les stats de session
- Intégration Gemini : génère un résumé automatique du tri
- Gestion de sessions avec stockage local (SQLite ou JSON)

---

## 💾 Frontend – Fonctionnalités

- 📷 **Webcam** ou **upload** local
- ✅ Affichage instantané de la prédiction
- 📈 **Dashboard temps réel**
  - Nombre de prunes triées
  - Graphiques par catégories
- ✨ **Génération de rapport textuel automatique**
- 📱 Responsive pour tablette & mobile

---

## 📆 Plan de travail – 6 Jours

### 🛠️ Jour 1 – Dataset & Setup
- Téléchargement et organisation des datasets : `cleaned_data`, `superclass_data`, `defect_data`
- Split stratifié (train/val/test)
- Environnement Python + GitHub

### 🧠 Jour 2 – Entraînement YOLOv8-cls
- Adapter dataset + entraînement
- Sauvegarder modèle et logs
- Premiers tests de précision

### 🧠 Jour 3 – Autres modèles
- Entraînement EfficientNetB0, MobileNetV2
- Comparaison modèles : précision / rapidité
- Sélection du modèle final

### 🛠️ Jour 4 – Backend + API
- FastAPI : endpoints + traitement images
- Intégration Gemini
- Système de session + statistiques
- Tests via Postman

### 🖼️ Jour 5 – Frontend + Dashboard
- Composants webcam, uploader, dashboard
- SSE ou polling pour maj temps réel
- Intégration Gemini et affichage résultat

### 🏰 Jour 6 – Finitions & Livraison
- Nettoyage
- Dockerisation (si temps)
- Vidéo de démo (≤ 2 min)
- Dépôt GitHub + soumission

---

## ✅ Checklist finale

| Élément              | Statut |
|----------------------|--------|
| Dataset nettoyé      | ⬜     |
| 3 modèles entraînés   | ⬜     |
| Modèle final prêt     | ⬜     |
| API FastAPI fonctionnelle | ⬜     |
| Gemini intégré        | ⬜     |
| Webcam / Upload React | ⬜     |
| Dashboard stats       | ⬜     |
| Rapport texte IA      | ⬜     |
| Démo vidéo & GitHub   | ⬜     |

---

## 📝 À améliorer après prototype

- Ajouter **object detection** pour gestion multiple fruits/image
- Contrôle caméra et redirection mécanique
- Authentification utilisateur
- Historique avancé + export CSV/PDF
- Multilangue (FR/EN)

