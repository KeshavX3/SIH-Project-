# 🌡️ HeatGuard AI — Extreme Heatwave Early Warning & Thermal Stress Intelligence Platform

[![Smart India Hackathon](https://img.shields.io/badge/SIH-2024%20%2F%20SIH26083-FF6B35?style=for-the-badge&logo=target)](https://sih.gov.in)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite%20%2B%20TS-61DAFB?style=for-the-badge&logo=react)](https://react.dev/)
[![PostgreSQL PostGIS](https://img.shields.io/badge/Database-PostGIS-336791?style=for-the-badge&logo=postgresql)](https://postgis.net/)
[![Docker](https://img.shields.io/badge/Orchestration-Docker%20Compose-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)

> **Smart India Hackathon (SIH) — Problem Statement SIH26083**  
> **Target Prototype City:** Jaipur, Rajasthan, India  
> An AI-driven early-warning and human thermal-stress decision-support system designed to protect vulnerable urban populations from extreme heatwaves.

---

## 📌 Table of Contents
1. [What We Are Building](#-what-we-are-building)
2. [Key Features & Capabilities](#-key-features--capabilities)
3. [Scientific & Algorithmic Foundation](#-scientific--algorithmic-foundation)
4. [System Architecture](#-system-architecture)
5. [What Has Been Completed So Far](#-what-has-been-completed-so-far)
6. [Repository Structure](#-repository-structure)
7. [How to Start & Run the Project](#-how-to-start--run-the-project)
   - [Method 1: Quickstart with Docker Compose (Recommended)](#method-1-quickstart-with-docker-compose-recommended)
   - [Method 2: Manual Local Setup (Backend + Frontend)](#method-2-manual-local-setup-backend--frontend)
8. [Default Demo Credentials & API Documentation](#-default-demo-credentials--api-documentation)
9. [Configuration & Environment Variables](#-configuration--environment-variables)
10. [Roadmap & Next Steps](#-roadmap--next-steps)

---

## 🎯 What We Are Building

Rising global temperatures and urban heat islands (UHI) present severe health hazards to vulnerable urban citizens, such as outdoor gig workers, construction laborers, senior citizens, and young children. Traditional meteorological warnings often only state dry-bulb temperature (e.g., "43°C"), failing to quantify the actual physiological strain felt by the human body when factoring in **humidity, wind speed, and solar radiation**.

**HeatGuard AI** bridges this critical gap by delivering:
- **Ward-level Hyperlocal Resolution:** Moving beyond city-wide generalizations to identify hyper-local hotspots across Jaipur's municipal wards.
- **Human Thermal Stress Metrics:** Calculating internationally recognized indices (Heat Index, WBGT, UTCI, and custom HTSI).
- **Vulnerability Mapping:** Combining demographic vulnerability (slum density, elderly population, outdoor workers) with green canopy cover and hospital accessibility.
- **Actionable City-Grade Mitigation:** Automated triggers for municipal emergency responses (cooling shelters, water stations, hospital surge staffing, SMS alerts).

---

## ✨ Key Features & Capabilities

| Feature | Description |
| :--- | :--- |
| 🗺️ **Interactive Ward Heat Map** | Leaflet-powered GIS dashboard showing ward boundaries, temperature heatmaps, and high-risk thermal zones across Jaipur. |
| 📊 **Real-time Analytics Dashboard** | Key metrics including current city temperature, average WBGT, active alerts, and population at severe risk. |
| 🧮 **What-If Thermal Simulator** | Interactive tool for policymakers and citizens to test custom micro-climate parameters and simulate human heat-stroke risk. |
| 🚨 **Early Warning & Alert Engine** | Multi-level automated alert dispatcher (Advisory, Caution, Heatwave Warning, Extreme Emergency) with escalation workflows. |
| 🏥 **Cooling Center & Hospital Allocation** | Geospatial tracking of municipal cooling centers, hydration posts, and healthcare surge capacity. |
| 🤖 **Machine Learning Risk Engine** | Predictive ML model trained to forecast ward-level health vulnerability scores. |
| 🔐 **Role-Based Access Control (RBAC)** | Secure JWT authentication with tiered roles: Municipal Administrators, Health Analysts, and General Public. |

---

## 🔬 Scientific & Algorithmic Foundation

The platform integrates standard biometeorological formulas:

1. **NOAA Heat Index (HI):** Rothfusz multiple regression model measuring apparent temperature based on temperature and relative humidity.
2. **Wet-Bulb Globe Temperature (WBGT):** Bernard & Pourmoghani outdoor solar-load approximation, assessing heat stress for outdoor manual labor.
3. **Universal Thermal Climate Index (UTCI):** Multi-node physiological thermal regulation approximation for outdoor thermal comfort.
4. **Human Thermal Stress Index (HTSI):** A composite multi-criteria index ($0 - 100$) integrating ambient climate, demographic vulnerability, and adaptive infrastructure capacity.

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    React 18 + Vite (Frontend)               │
│  - Leaflet GIS Heatmaps       - Interactive Thermal Sim     │
│  - Ward Analytics & Recharts  - Alert Dispatch Management   │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST APIs (JSON / JWT)
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI (Backend Service)                │
│  - /api/thermal (Indices)     - /api/weather (Sensors)      │
│  - /api/wards (GeoJSON/GIS)   - /api/alerts (Notification)  │
│  - /api/ml (Predictions)      - /api/dashboard (Summaries)  │
├─────────────────────────────────────────────────────────────┤
│   Core Engines: Thermal Engine | Risk Engine | ML Predictor │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLAlchemy + GeoAlchemy2
┌──────────────────────────────▼──────────────────────────────┐
│               PostgreSQL 15 + PostGIS Database              │
│  - Spatial Ward Boundaries    - Weather History Timeseries  │
│  - Demographic Records        - Real-time Alert Logs        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 What Has Been Completed So Far

- [x] **Backend Infrastructure:** Complete FastAPI modular architecture with routers, dependency injection, and Pydantic schemas.
- [x] **Database & PostGIS:** Relational models for Wards, Demographics, Weather, ThermalMetrics, Alerts, and Hospitals.
- [x] **Automated Data Seeder:** Automated bootstrapping script (`seed_demo.py`) that populates realistic synthetic Jaipur ward data, weather logs, and demo user accounts on startup.
- [x] **Core Calculation Engines:**
  - `thermal_engine.py`: Full implementations of Heat Index, WBGT, and UTCI.
  - `risk_engine.py` & `vulnerability.py`: Demographic and environmental risk scoring.
  - `predict.py` & `train.py`: Pre-trained ML pipeline and risk scoring engine.
- [x] **Frontend Web Application:**
  - Responsive dark-mode UI styled with TailwindCSS and Lucide Icons.
  - **Overview Dashboard:** Real-time health metrics, active alerts, and risk level breakdown.
  - **Jaipur GIS Map:** Ward polygons, color-coded heat stress indicators, and interactive ward inspector.
  - **Thermal Simulator:** Dynamic sliders for temperature, humidity, wind, and radiation with live gauge updates.
  - **Ward Analytics:** In-depth breakdown per municipal zone.
  - **Alerts Management:** Workflow to acknowledge, escalate, or resolve municipal heat warnings.
- [x] **Dockerization:** Complete `docker-compose.yml` orchestrating Database, Backend, and Frontend.

---

## 📂 Repository Structure

```text
SIH-Project-/
├── backend/
│   ├── alembic/                 # Database migration scripts
│   ├── app/
│   │   ├── alerts/              # Alert dispatch & notification logic
│   │   ├── api/                 # API routes (auth, thermal, wards, weather, ml)
│   │   ├── core/                # App config, security & JWT handling
│   │   ├── database/            # Database engine & session management
│   │   ├── ml/                  # ML training and inference pipelines
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── risk/                # Vulnerability and risk evaluation engines
│   │   ├── schemas/             # Pydantic data validation schemas
│   │   ├── seeds/               # Initial demo data seeder (Jaipur wards)
│   │   ├── thermal/             # Mathematical heat & thermal stress formulas
│   │   └── main.py              # FastAPI application entry point
│   ├── tests/                   # Backend unit tests
│   ├── Dockerfile               # Backend container recipe
│   └── requirements.txt         # Python dependencies
├── data/
│   └── geojson/
│       └── jaipur_wards.geojson # Spatial boundaries for Jaipur wards
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI widgets
│   │   │   ├── alerts/          # Alert management UI
│   │   │   ├── calculator/      # Thermal index simulator
│   │   │   ├── dashboard/       # Metric cards & risk distribution
│   │   │   ├── layout/          # Navigation bar & headers
│   │   │   ├── map/             # Leaflet heat map components
│   │   │   └── wards/           # Ward-level analytical breakdown
│   │   ├── services/            # Axios API client & fallback state
│   │   ├── types/               # TypeScript interfaces
│   │   ├── App.tsx              # Main UI controller & state
│   │   └── index.css            # Tailwind & custom glassmorphism styles
│   ├── Dockerfile               # Production Nginx frontend container
│   ├── package.json             # NPM dependencies
│   └── vite.config.ts           # Vite bundler configuration
├── docker-compose.yml           # Unified multi-container orchestration
├── .env.example                 # Template for configuration settings
└── README.md                    # Project documentation
```

---

## ⚡ How to Start & Run the Project

### Method 1: Quickstart with Docker Compose (Recommended)

Make sure you have **Docker Desktop** installed and running.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KeshavX3/SIH-Project-.git
   cd SIH-Project-
   ```

2. **Launch all services:**
   ```bash
   docker compose up --build
   ```

3. **Access the application:**
   - **Frontend UI:** [http://localhost:3000](http://localhost:3000)
   - **FastAPI Backend:** [http://localhost:8000](http://localhost:8000)
   - **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **System Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

*(The database will be automatically created, migrated, and seeded with Jaipur ward data on initial startup).*

---

### Method 2: Manual Local Setup (Backend + Frontend)

#### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- PostgreSQL 14+ with PostGIS extension enabled (or run only DB via Docker)

#### 1. Setup Backend:
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (or copy .env.example from root)
cp ../.env.example .env

# Run FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Setup Frontend:
Open a second terminal window:
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```

The frontend will run at [http://localhost:5173](http://localhost:5173) (or `3000`) and connect automatically to `http://localhost:8000`.

---

## 🔑 Default Demo Credentials & API Documentation

The demo seeder auto-creates the following credentials for testing:

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@heatguard.ai` | `heatguard2024` | Full system access, alert dispatch & override |
| **Health Analyst** | `analyst@heatguard.ai` | `analyst2024` | Read analytics, run simulations, view GIS |

### Key API Endpoints

- `GET /api/health` — Service readiness & status check
- `GET /api/dashboard/summary` — High-level statistics and city summary
- `GET /api/wards` — List of all Jaipur wards with risk and thermal scores
- `GET /api/wards/{id}/geojson` — Spatial polygon data for mapping
- `POST /api/thermal/calculate` — Compute Heat Index, WBGT, UTCI for arbitrary inputs
- `GET /api/alerts` — Fetch currently active heat warnings
- `POST /api/alerts/{id}/acknowledge` — Acknowledge and update alert status

---

## ⚙️ Configuration & Environment Variables

Create a `.env` file in the root directory based on `.env.example`:

```env
# Database Settings
POSTGRES_DB=heatguard
POSTGRES_USER=heatguard
POSTGRES_PASSWORD=heatguard_secret_2024
DATABASE_URL=postgresql://heatguard:heatguard_secret_2024@localhost:5432/heatguard

# Security
JWT_SECRET=your-super-secret-jwt-key-change-in-production-minimum-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Application Configuration
DEMO_MODE=true
APP_ENV=development
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# ML & Services
ML_MODEL_PATH=app/ml/models/risk_model.pkl
NOTIFICATION_MODE=mock
```

---

## 🛣️ Roadmap & Next Steps

- [ ] **Live IoT Weather Station Integration:** Ingest live AWS / IMD (India Meteorological Department) weather feeds.
- [ ] **Automated SMS/WhatsApp Broadcasts:** Integration with Twilio / Govt SMS gateway for outdoor laborer notifications.
- [ ] **Dynamic Cooling Center Routing:** Directions for citizens to the nearest operational cooling center via mobile view.
- [ ] **Multi-City Expansion:** Scaling beyond Jaipur to other heat-vulnerable Indian cities (Ahmedabad, Delhi, Nagpur, Hyderabad).

---

## 👥 Contributors & Hackathon Team

- **Project:** HeatGuard AI
- **Hackathon:** Smart India Hackathon (SIH)
- **Problem ID:** SIH26083

---

*Disclaimer: In demo mode, all weather readings and ward predictions utilize realistic synthetic datasets generated for proof-of-concept and competition evaluation.*
