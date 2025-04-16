# PlumVision – JCIA Hackathon 2025

## Table of Contents
- [PlumVision – JCIA Hackathon 2025](#plumvision--jcia-hackathon-2025)
  - [Table of Contents](#table-of-contents)
  - [What is PlumVision?](#what-is-plumvision)
  - [Objective (Prototype)](#objective-prototype)
  - [Key Features (Prototype)](#key-features-prototype)
  - [Technical Stack (Prototype)](#technical-stack-prototype)
  - [System Architecture (Prototype)](#system-architecture-prototype)
    - [Key Components](#key-components)
    - [Data Flow](#data-flow)
  - [Typical Use Case (Prototype – Demonstration)](#typical-use-case-prototype--demonstration)
  - [Backend – Functionality (Prototype)](#backend--functionality-prototype)
  - [Frontend – Features (Prototype)](#frontend--features-prototype)
  - [Work Plan – 6 Periods to Build the Prototype](#work-plan--6-periods-to-build-the-prototype)
    - [Period 1 – Dataset \& Preparation](#period-1--dataset--preparation)
    - [Period 2 – Model Selection and Training](#period-2--model-selection-and-training)
    - [Period 3 – Backend Development (API and Real-Time Tracking)](#period-3--backend-development-api-and-real-time-tracking)
    - [Period 4 – Frontend Development (User Interface, Camera Feed, and Statistics)](#period-4--frontend-development-user-interface-camera-feed-and-statistics)
    - [Period 5 – Integration and Testing](#period-5--integration-and-testing)
    - [Period 6 – Demo and Presentation Preparation](#period-6--demo-and-presentation-preparation)
  - [Final Checklist (Prototype)](#final-checklist-prototype)
  - [Database Structure (SQLite/SQLAlchemy - Prototype)](#database-structure-sqlitesqlalchemy---prototype)
  - [Backend Tools](#backend-tools)
  - [Current Project Structure](#current-project-structure)
  - [Team](#team)

---

## What is PlumVision?

**PlumVision** is an intelligent solution designed to automate the sorting of African plums. This prototype aims to demonstrate the feasibility of real-time plum classification using machine learning models and an interactive user interface.

---

## Objective (Prototype)

Develop a prototype capable of classifying African plums in real-time via a connected camera into one of **6 main categories**: good quality, unripe, spotted, cracked, bruised, rotten. The main objective is to demonstrate real-time classification functionality, session statistics tracking, and provide a basic user interface for interaction and visualization of results.

---

## Key Features (Prototype)

* **Real-Time Classification:** Analysis of video feed from a connected camera to classify plums.
* **Image Upload:** Ability to upload a plum image for a single prediction.
* **Session Statistics:** Real-time tracking of the total number of plums processed and their distribution by category during a scanning session.
* **Interactive User Interface:** Simple web interface to start/stop sessions, visualize the camera feed, predictions, and statistics.
* **AI Comments:** Automatic generation of comments on overall sorting quality.

---

## Technical Stack (Prototype)

| Component | Tools / Languages |
|-----------|-------------------|
| **ML Models** | PyTorch, YOLOv8-cls, EfficientNetB0, RexNet, MobileNetV3, ... |
| **Backend API** | **FastAPI** (for speed and features) + Uvicorn (ASGI server) |
| **Frontend** | **React** + Axios + Chart.js |
| **Real-Time** | **WebSockets** (bidirectional communication and continuous data flow) |
| **Training** | Jupyter Notebooks + PyTorch + Python Scripts |
| **Storage/DB** | SQLite/SQLAlchemy (Prototype) |
| **Dataset** | African Plums Dataset (Kaggle) |

---

## System Architecture (Prototype)

```
┌─────────────────┐                ┌────────────────────────────┐
│                 │                │                            │
│   React         │◄────REST API───┤   FastAPI Backend          │
│   Frontend      │                │   - Image classification   │
│                 │                │   - Session management     │
│   - UI          │◄───────────────┤   - Statistics tracking    │
│   - Camera feed │     WebSockets │                            │
│   - Dashboards  │───────────────►│   - Database (SQLite)      │
│   - Statistics  │                │                            │
│                 │                │                            │
└─────────────────┘                └─────────────┬──────────────┘
                                                 │
                                                 │
                                                 ▼
                                    ┌────────────────────────────┐
                                    │                            │
                                    │  PyTorch Models            │
                                    │  - PlumVision Classifier   │
                                    │  - MobileNetV3/ReXNet/YOLO │
                                    │                            │
                                    └────────────────────────────┘
```

The system comprises a **React** frontend for the user interface, a **FastAPI** backend for the API and classification logic, and real-time communication via **WebSockets** for the camera feed and statistics tracking. The bidirectional WebSocket connection allows for continuous data flow between the frontend and backend components.

### Key Components

**Frontend (React)**
- User interface for interaction
- Camera feed capture and display
- Real-time statistics visualization
- Session management controls

**Backend (FastAPI)**
- REST API endpoints for prediction requests
- WebSocket server for real-time video processing
- Session statistics tracking and storage
- Database integration with SQLite

**Machine Learning**
- PyTorch-based image classification models
- Trained on African plums dataset
- Multiple model architectures to implement (MobileNetV3, ReXNet, YOLO)

### Data Flow
1. User starts a scanning session via the frontend
2. Camera feed is captured and frames are sent to backend via WebSockets
3. Backend processes images with PyTorch models
4. Classification results and updated statistics are sent back to frontend
5. Frontend displays results in real-time dashboards
6. Session data is stored in SQLite database for later retrieval

---

## Typical Use Case (Prototype – Demonstration)

> **Prototype demonstration:**
>
> 1. The user launches the web application.
> 2. In the prediction section, the user **starts a real-time scanning session**, allowing access to the connected camera.
> 3. The frontend **captures images** from the video feed at a determined frequency and sends them to the backend via WebSockets.
> 4. The backend **classifies** each plum (via the selected model) and **updates the session statistics** (total number of images processed, number of plums predicted per category).
> 5. The backend **sends these statistics** to the frontend in real-time.
> 6. The interface displays in real-time:
>    * The camera feed.
>    * The predicted category for each detected plum (potentially overlaid).
>    * A **dedicated section displaying current session statistics** (total number of plums, distribution by category).
> 7. The user has the option to **stop the scanning session** at any time.

---

## Backend – Functionality (Prototype)

* **/predict**: receives an image (upload), returns the prediction.
* **/stream**: manages the camera video feed via **WebSockets**.
    * Receives images captured by the frontend.
    * Makes a prediction on each image.
    * **Maintains counters in memory for the current session:**
        * Total number of images processed.
        * Number of predictions per category.
    * **Returns to the frontend:**
        * The prediction for the current image (potentially).
        * Updated session statistics.
* **/metrics**: returns the current session statistics (total count, distribution).
* **Session Management**: manages the session state (active/inactive) and stores session data in memory or in a temporary SQLite/SQLAlchemy file.

---

## Frontend – Features (Prototype)

* **Presentation Section:** Concise description of the PlumVision project and team member names.
* **Prediction Section:**
    * Ability to **upload an image** for instant prediction.
    * **Real-time scanning session:**
        * Button to **start** and **stop** the session.
        * Access to the user's camera (via browser API).
        * Display of the video feed in a `<video>` element.
        * **Capture of images from the video feed at a determined frequency.**
        * Sending captured images to the backend via WebSockets.
        * Real-time display of the camera feed and predictions overlaid or displayed alongside.
        * **Real-time display of session statistics:**
            * Total number of plums processed.
            * Distribution by category (as text or a simple graph).
* **Dashboard Section:**
    * Display of **total number of plums processed** during the session (after it's stopped).
    * A **simple chart (Chart.js)** showing the distribution of plums by category for the current session (after it's stopped).

---

## Work Plan – 6 Periods to Build the Prototype

### Period 1 – Dataset & Preparation
* Selection and organization of a representative subset of the dataset for the prototype.
* Verification and preparation of data for training and quick tests.
* Setup of the development environment and version control (GitHub).

### Period 2 – Model Selection and Training
* Choice of a main model (**YOLOv8-cls** or **EfficientNetB0**) for the prototype, based on initial accuracy and speed tests.
* Adaptation of the dataset to the format required by the chosen model.
* Quick training of the model on the data subset.
* Saving of the trained model.

### Period 3 – Backend Development (API and Real-Time Tracking)
* Setting up an API with **FastAPI**.
* Creation of a **/predict** endpoint to receive an image and return the model's prediction.
* Implementation of session data management (in memory or via **SQLite/SQLAlchemy**), including tracking of the total number of images processed and predictions by category.
* Creation of a **/metrics** endpoint to return session statistics.
* **Implementation of WebSockets management for real-time camera feed**, including receiving images, prediction, updating session statistics, and sending these statistics to the frontend.

### Period 4 – Frontend Development (User Interface, Camera Feed, and Statistics)
* Creation of the basic structure of the **React** application with three sections (Presentation, Prediction, Dashboard).
* Implementation of the image upload functionality in the Prediction section.
* **Implementation of real-time scanning session management in the Prediction section:**
    * Start and stop session buttons.
    * Access to the user's camera.
    * Display of the video feed.
    * **Capture of images at a determined frequency (for example, every 0.5 seconds).**
    * **Establishment and management of WebSocket connection with the backend.**
    * **Sending captured images to the backend via WebSockets.**
    * **Real-time display of session statistics received from the backend.**

### Period 5 – Integration and Testing
* Complete integration of the frontend with the backend, including real-time camera feed and statistics updates via WebSockets.
* Thorough functional testing of the entire prototype (upload, prediction, real-time scanning, statistics display, session start/stop).
* Optimization of the real-time flow for minimal latency and efficient resource management.
* Bug fixes and user interface improvements.

### Period 6 – Demo and Presentation Preparation
* Preparation of a short demo video of the prototype (≤ 2 min) highlighting real-time operation and statistics display.
* Creation of a concise presentation highlighting the prototype's features and results.
* Finalization of the GitHub repository for submission.

---

## Final Checklist (Prototype)

| Item | Status |
|------|--------|
| Dataset selected and prepared | **Done** |
| Main model trained and saved | **Done** |
| Functional FastAPI API with prediction | **Done** |
| Session data management with statistics tracking | **Done** |
| Functional /metrics endpoint | **Done** |
| Frontend Presentation section | **Done** |
| Image upload functionality | **Done** |
| **Camera access, image capture, and functional real-time feed** | **Done** |
| Frontend-Backend communication via WebSockets for feed and stats | **Done** |
| **Real-time display of session statistics on the frontend** | **Done** |
| Session start and stop functionality | **Done** |
| Dashboard section with statistics (after session stop) | **Done** |
| Demo video prepared | ⬜ |
| Presentation prepared | ⬜ |
| GitHub repository ready for submission | ⬜ |

---

## Database Structure (SQLite/SQLAlchemy - Prototype)

For the prototype, a simple structure with just one or two tables to store session information.

**Table: `sessions`**

| Column | Type | Description |
|--------|------|-------------|
| `session_id` | INTEGER | Primary key, unique session identifier |
| `start_time` | DATETIME | Session start timestamp |
| `end_time` | DATETIME | Session end timestamp |
| `total_plums` | INTEGER | Total number of plums processed |
| `category_counts` | TEXT | JSON string representing the count by category |

**Table: `predictions` (For more detailed history)**

| Column | Type | Description |
|--------|------|-------------|
| `prediction_id` | INTEGER | Primary key, unique prediction identifier |
| `session_id` | INTEGER | Foreign key referencing the `sessions` table |
| `image_name` | TEXT | Image filename |
| `predicted_class` | TEXT | Predicted category for the plum |
| `prediction_time` | DATETIME | Prediction timestamp |

For the prototype, we could start by storing session data in an in-memory dictionary and consider **SQLite/SQLAlchemy** if we want basic persistence between API executions.

---

## Backend Tools

To achieve our objectives, I propose **FastAPI** as the main backend framework. Its asynchronous nature and good integration with **WebSockets** make it a judicious choice for managing real-time data flow and statistics updates.

For WebSockets management in FastAPI, we can use the built-in features based on **Starlette**. We'll need to define a WebSocket endpoint that will handle the connection, image reception, prediction execution, session counter updates, and sending statistics to the frontend.

Additionally:

* **Uvicorn:** Will be our ASGI server to run the FastAPI application, for good performance for asynchronous and WebSocket applications.
* **PyTorch:** For loading and executing our deep learning model for prediction.
* **SQLite/SQLAlchemy:** For basic session data storage.

For the frontend:

* **React:** A robust JavaScript library for building dynamic and reactive user interfaces, to manage the camera feed, WebSocket communication, and real-time statistics display.
* **TailwindCSS:** For quickly styling the user interface.
* **Axios:** For making requests to the backend API (for image upload and potentially for retrieving session statistics after stopping).
* **Chart.js:** For simple and efficient chart creation to visualize the distribution of plum categories.

---

## Current Project Structure

```bash
├── JCIA_PLUM_DATA_CHALLENGE/
│   ├── .gitattributes
│   ├── .gitignore
│   ├── Plan.md
│   ├── prompt.txt
│   ├── untrack.sh
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
│   │   ├── Sets/
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
│   │   ├── superclass_data/
│   │   │   ├── class_weights.json
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
│   │   │   ├── CustomEfficientNet/
│   │   │   ├── CustomRexNet/
│   │   │   ├── efficientnetlite/
│   │   │   │   ├── defects/
│   │   │   │   ├── global/
│   │   │   │   ├── superclass/
│   │   │   ├── rexnet/
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
│   │   ├── EXPLORATION/
│   │   │   ├── DefectClassesSplit.ipynb
│   │   │   ├── Exploration.ipynb
│   │   │   ├── SuperClassSplit.ipynb
│   │   ├── REXNET_Experimentation/
│   │   │   ├── RexNetTraining.ipynb
│   │   │   ├── RexNet_Contrast.ipynb
│   │   ├── TRIPLET_Experimentation/
│   │   │   ├── CustomApproach.ipynb
│   │   ├── YOLO_Experimentation/
│   │   │   ├── DefectClassTraining.ipynb
│   │   │   ├── SuperClassTraining.ipynb
│   │   │   ├── YoloTraining.ipynb
│   ├── Plums/
│   │   ├── 1.jpeg
│   │   ├── 2.jpeg
│   │   ├── 3.jpeg
│   │   ├── 4.jpeg
│   │   ├── 5.jpeg
│   │   ├── 6.jpeg
│   ├── utilities/
│   │   ├── CustomDatasetLoader.py
│   │   ├── CustomEvaluation.py
│   │   ├── CustomTraining.py
│   │   ├── Helper.py
│   │   ├── PlumSetEval.py
│   │   ├── RunsEvaluator.py
│   │   ├── __init__.py
│   │   ├── utils.py
```

---

## Team

*PlumVision*