# 🛡️ HoneyCloud Sentinel

> **AI-Driven Adaptive Honeypot Intelligence Platform for Real-Time Cyber Threat Detection**

*Turning attacker behavior into actionable cyber intelligence.*

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat-square&logo=next.js)
![Kafka](https://img.shields.io/badge/Apache_Kafka-3.0+-red?style=flat-square&logo=apachekafka)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.0+-orange?style=flat-square&logo=tensorflow)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [ML Models](#ml-models)
- [Screenshots](#screenshots)
- [Team](#team)

---

## Overview

HoneyCloud Sentinel is a production-grade cybersecurity platform that
deploys AI-powered honeypots to attract, detect, analyze, and predict
cyber attacks in real time.

The system captures attacker behavior through decoy services, processes
attack data through a scalable Kafka pipeline, runs three ML models for
classification and anomaly detection, maps every attack to the MITRE
ATT&CK framework, and displays everything on a live SOC-grade dashboard.

**Built for:** National Level Hackathon — Blue Team Challenge

---

## Architecture
```
Internet Attackers
        │
        ▼
┌───────────────────┐
│  Honeypot Layer   │  SSH · HTTP · FTP · IoT · Database
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   Apache Kafka    │  High-throughput log streaming
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   ML Engine       │  Isolation Forest · Random Forest · K-Means
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  MITRE ATT&CK     │  Maps every attack to framework techniques
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Multi-Agent AI   │  4-agent TI pipeline via Groq LLM
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  LSTM Predictor   │  Predicts next attack from sequence
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  SOC Dashboard    │  Next.js · Real-time map · Charts
└───────────────────┘
```

---

## Features

### 🔴 Core Detection
- **SSH Honeypot** — captures brute force and credential attacks
- **Real-time Kafka pipeline** — streams attack logs instantly
- **IP Geolocation** — maps every attacker to their country and city

### 🤖 AI/ML Engine
- **Isolation Forest** — detects zero-day and anomalous attacks
- **Random Forest** — classifies attack type with confidence score
- **K-Means Clustering** — groups attacks into campaigns
- **LSTM Neural Network** — predicts the next likely attack

### 🗺️ MITRE ATT&CK Integration
- Every attack mapped to official framework techniques
- Interactive heatmap showing active tactics
- Direct links to attack.mitre.org for each technique

### 🕵️ Multi-Agent Threat Intelligence
- **Agent 1** — Log Analyzer: extracts IoCs
- **Agent 2** — Threat Investigator: identifies campaigns
- **Agent 3** — Risk Analyst: assesses business impact
- **Agent 4** — Response Recommender: generates actions

### 📊 SOC Dashboard
- Live attack map with geolocation markers
- Resizable panels with drag handles
- Real-time attack feed with MITRE IDs
- Risk gauge and stat cards
- Attack prediction panel

### 📄 AI Report Generator
- One-click HTML report with charts and risk gauge
- Downloadable dark-themed PDF
- LLM-written professional threat analysis via Groq

---

## Tech Stack

| Layer | Technology |
|---|---|
| Honeypots | Python sockets, T-Pot |
| Streaming | Apache Kafka, Filebeat |
| Backend | Python, FastAPI, Uvicorn |
| ML Models | Scikit-learn, TensorFlow, XGBoost |
| AI Pipeline | Groq API, Llama 3.3 70B |
| Frontend | Next.js 14, Tailwind CSS, shadcn/ui |
| Charts | Recharts, Leaflet |
| Reports | ReportLab, HTML/CSS |
| DevOps | Docker, Docker Compose |
| Threat Intel | MITRE ATT&CK, ip-api.com |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker Desktop
- Git

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/HoneyCloud-Sentinel.git
cd HoneyCloud-Sentinel
```

### 2. Set up Python environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
# Get a free key at console.groq.com
```

### 4. Start Kafka
```bash
docker-compose up -d
```

### 5. Train ML models
```bash
python scripts/train_all_models.py
python scripts/train_lstm.py
```

### 6. Start the API
```bash
uvicorn api.threat_api:app --reload --host 0.0.0.0 --port 8000
```

### 7. Start the dashboard
```bash
cd dashboard
npm install
npm run dev
```

### 8. Run the demo
```bash
# In a new terminal
python scripts/demo.py
```

Open **http://localhost:3000** to see the live dashboard.

---

## Project Structure
```
HoneyCloud-Sentinel/
│
├── api/
│   ├── threat_api.py          # FastAPI — all endpoints
│   └── attack_store.py        # In-memory attack + investigation store
│
├── honeypots/
│   └── ssh_honeypot.py        # SSH decoy service
│
├── data_pipeline/
│   ├── kafka_producer.py      # Sends logs to Kafka
│   └── kafka_consumer.py      # Reads logs for ML
│
├── ml_models/
│   ├── feature_engineering.py # Raw log → ML features
│   ├── anomaly_detection.py   # Isolation Forest
│   ├── attack_classifier.py   # Random Forest
│   ├── clustering.py          # K-Means campaigns
│   ├── risk_scorer.py         # 0-100 risk scoring
│   └── attack_predictor.py    # LSTM next-attack prediction
│
├── ai_agents/
│   ├── mitre_mapper.py              # MITRE ATT&CK mapping
│   ├── threat_intelligence_agent.py # 4-agent investigation
│   ├── threat_report_agent.py       # Groq LLM report writer
│   ├── html_report_generator.py     # Visual HTML report
│   └── pdf_generator.py             # Dark-themed PDF
│
├── dashboard/                 # Next.js frontend
│   ├── app/
│   │   ├── page.tsx           # Main dashboard
│   │   └── globals.css        # Dark SOC theme
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── StatCards.tsx
│   │   ├── AttackMap.tsx      # Leaflet world map
│   │   ├── Charts.tsx
│   │   ├── MitreHeatmap.tsx
│   │   ├── InvestigationPanel.tsx
│   │   ├── PredictionPanel.tsx
│   │   ├── AttackFeed.tsx
│   │   └── ReportButton.tsx
│   └── lib/
│       └── api.ts             # All API calls
│
├── scripts/
│   ├── demo.py                # 5-phase attack demo
│   ├── train_all_models.py    # Train RF + IF + KMeans
│   ├── train_lstm.py          # Train LSTM predictor
│   └── test_pipeline.py       # Quick pipeline test
│
├── datasets/
│   └── README.md              # Dataset download links
│
├── models/                    # Saved trained models
│   ├── anomaly_detector.pkl
│   ├── attack_classifier.pkl
│   ├── clustering.pkl
│   └── lstm_predictor.keras
│
├── docker-compose.yml         # Kafka + Zookeeper
├── requirements.txt
├── .env.example
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API info and endpoint list |
| GET | `/health` | System health check |
| POST | `/analyze` | Analyze single attack through ML |
| GET | `/attacks` | Recent attacks with ML results |
| GET | `/stats` | Aggregated attack statistics |
| GET | `/live` | SSE stream for real-time updates |
| GET | `/mitre/heatmap` | ATT&CK tactic frequency data |
| GET | `/mitre/detail/{type}` | Full MITRE entry for attack type |
| GET | `/investigations` | TI agent investigation reports |
| POST | `/investigate` | Manually trigger TI investigation |
| GET | `/predict/next` | LSTM next attack prediction |
| POST | `/predict/train` | Retrain LSTM on current data |
| GET | `/report/html` | Visual HTML threat report |
| GET | `/report/generate` | Download PDF threat report |
| DELETE | `/attacks/clear` | Reset attack store |

Interactive docs: **http://localhost:8000/docs**

---

## ML Models

### Isolation Forest — Anomaly Detection
Trained on 451,000 real honeypot attacks. Detects unusual patterns
that don't match known attack behavior — effective for zero-day detection.

### Random Forest — Attack Classification
Uses port-based labeling to classify attacks into 6 categories:
SSH Brute Force, Web Exploit, Database Attack, FTP Attack,
Port Scan, Telnet Attack.

### K-Means Clustering — Campaign Detection
Groups attacks with similar feature patterns to identify coordinated
botnet campaigns and repeated attacker strategies.

### LSTM Neural Network — Attack Prediction
Learns temporal attack sequences to predict the next likely attack type.
Uses the last 10 attacks as input and outputs probability distribution
across all attack classes.

---

## Datasets

| Dataset | Size | Source |
|---|---|---|
| AWS Honeypot Attack Data | 451,581 events | Kaggle |
| CIC Honeynet Dataset | Large-scale T-Pot data | honeynetproject.com |
| Hornet 40 Dataset | 40 days, 8 locations | data.mendeley.com |
| Dionaea Honeypot Dataset | Malware + exploits | Kaggle |

---

## Demo

Run the 5-phase attack simulation:
```bash
python scripts/demo.py
```

| Phase | Description | Duration |
|---|---|---|
| 1 | Initial reconnaissance — slow port scans | 15s |
| 2 | Botnet campaign — 20 coordinated IPs | 10s |
| 3 | APT scenario — same IP, multiple vectors | 20s |
| 4 | Mass attack flood — 40 rapid attacks | 8s |
| 5 | Critical DB breach — 3 simultaneous hits | 5s |

Quick demo (30 seconds):
```bash
python scripts/demo.py --quick
```

Reset dashboard between runs:
```bash
curl -X DELETE http://localhost:8000/attacks/clear
```

---

## Environment Variables

Create a `.env` file in the project root:
```env
GROQ_API_KEY=gsk_your-key-here
```

Get a free Groq API key at **console.groq.com** — no credit card needed.

---

## Ethical Considerations

- Honeypots only simulate vulnerable environments
- No real user data is exposed
- All captured malware is isolated in sandboxes
- Attack data is anonymized before any sharing
- No offensive actions are taken against attackers
- Complies with responsible cybersecurity research practices

---

## Future Work

1. **Global Honeypot Network** — deploy across multiple cloud regions
2. **T-Pot Integration** — connect to real cloud honeypot platform
3. **CERT-In Integration** — share threat signatures nationally
4. **Automated Defense** — auto-update firewall rules from detections
5. **Full MITRE Coverage** — map all 14 ATT&CK tactic categories

---

*HoneyCloud Sentinel — Transforming attacker behavior into
actionable cyber intelligence.*