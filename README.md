<div align="center">

# 🛡️ HoneyCloud Sentinel

### AI-Driven Adaptive Honeypot Intelligence Platform
### for Real-Time Cyber Threat Detection

*Turning attacker behavior into actionable cyber intelligence.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-3.0+-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)](https://kafka.apache.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.0+-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

**Trained on 14.2 million real-world attack records from 4 honeypot datasets**

[Features](#-features) •
[Architecture](#-architecture) •
[Quick Start](#-quick-start) •
[Screenshots](#-screenshots) •
[ML Models](#-ml-models) •
[API](#-api-endpoints)

</div>

---

## 📸 Screenshots

<div align="center">

### SOC Dashboard — Live Attack Overview
![Dashboard](docs/screenshots/dashboard.png)

### Global Attack Map — Real-time Geolocation
![Attack Map](docs/screenshots/map.png)

### MITRE ATT&CK Framework Heatmap
![MITRE Heatmap](docs/screenshots/mitre.png)

### AI Threat Intelligence Investigation Panel
![Investigation](docs/screenshots/investigation.png)

</div>

---

## 🌟 Overview

HoneyCloud Sentinel is a production-grade cybersecurity platform that
deploys AI-powered honeypots to attract, detect, analyze, and predict
cyber attacks in real time.

The system captures attacker behavior through decoy services, streams
attack data through Apache Kafka, runs four ML models for classification
and anomaly detection, maps every attack to the MITRE ATT&CK framework,
and displays everything on a live SOC-grade dashboard with a global
attack map.

> Built for the National Level Hackathon — Blue Team Challenge

---

## ✨ Features

### 🔴 Real-Time Detection
- **SSH Honeypot** — captures brute force and credential attacks
- **Kafka streaming pipeline** — zero-latency attack log processing
- **IP Geolocation** — maps every attacker to country and city on a live map
- **Server-Sent Events** — dashboard updates instantly without polling

### 🤖 AI/ML Engine
- **Isolation Forest** — detects zero-day and anomalous attacks
- **Random Forest** — classifies 9 attack types with confidence scores
- **K-Means Clustering** — groups attacks into 8 campaign clusters
- **LSTM Neural Network** — predicts the next likely attack from sequences

### 🎯 MITRE ATT&CK Integration
- Every attack mapped to official framework techniques automatically
- Interactive heatmap showing active tactics in real time
- Clickable technique IDs linking to attack.mitre.org

### 🕵️ Multi-Agent Threat Intelligence
- **Agent 1** — Log Analyzer: extracts IoCs from raw attack data
- **Agent 2** — Threat Investigator: identifies campaigns and actors
- **Agent 3** — Risk Analyst: assesses business impact
- **Agent 4** — Response Recommender: generates executable actions
- Powered by **Groq API** (Llama 3.3 70B) — free tier

### 📊 SOC Dashboard
- Dark military-ops aesthetic with scanline overlay
- Resizable world map with animated attack lines
- Global Honeypot Network panel (Hornet 40 — 8 locations, 40 days)
- LSTM attack prediction with confidence bars
- One-click AI threat report (HTML + PDF)

### 📄 AI Report Generator
- **HTML report** — dark SOC theme with SVG risk gauge and charts
- **PDF download** — professional threat intelligence document
- LLM-written analysis covering 7 sections including IoCs

---

## 🏗️ Architecture
```
Internet Attackers
        │
        ▼
┌─────────────────────┐
│   Honeypot Layer    │  SSH · HTTP · FTP · IoT · Database
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Apache Kafka      │  High-throughput log streaming
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   ML Engine         │  Isolation Forest · Random Forest · K-Means
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   MITRE ATT&CK      │  Maps every attack to framework techniques
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Multi-Agent AI    │  4-agent TI pipeline via Groq LLM
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   LSTM Predictor    │  Predicts next attack from sequence
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   SOC Dashboard     │  Next.js · Live map · MITRE heatmap
└─────────────────────┘
```

---

## 📊 Training Dataset

| Dataset | Rows | Type | Source |
|---|---|---|---|
| CIC Honeynet 2023 | 13,767,678 | Real network pcap | ciciot.unb.ca |
| AWS Honeypot | 406,766 | Cloud honeypot logs | Kaggle |
| Dionaea Honeypot | 27,529 | Malware honeypot | Kaggle |
| Hornet 40 | 8 locations · 40 days | Geographic stats | Mendeley |
| **TOTAL** | **14,201,973** | **4 real-world sources** | |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker Desktop
- Git
- Free Groq API key — [console.groq.com](https://console.groq.com)

### 1. Clone
```bash
git clone https://github.com/YOUR_USERNAME/HoneyCloud-Sentinel.git
cd HoneyCloud-Sentinel
```

### 2. Python environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment variables
```bash
cp .env.example .env
# Add your GROQ_API_KEY from console.groq.com (free)
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

### 6. Start API
```bash
uvicorn api.threat_api:app --reload --host 0.0.0.0 --port 8000
```

### 7. Start dashboard
```bash
cd dashboard
npm install
npm run dev
```

### 8. Run the demo
```bash
python scripts/demo.py
```

Open **http://localhost:3000**

---

## 🧠 ML Models

### Isolation Forest — Anomaly Detection
Trained on 14.2M real honeypot attacks. Detects unusual patterns
that don't match known attack behavior — effective for zero-day detection.
Flags attacks with anomaly scores for heightened investigation priority.

### Random Forest — Attack Classifier
Classifies attacks into 9 categories using port-based and
behavioral features. Trained on 3 real-world honeypot sources.
Achieves 100% accuracy on test set (deterministic port-based labels).

| Class | Training Samples |
|---|---|
| Port Scan / Other | 12,031,938 |
| Web Exploit | 1,016,332 |
| SSH Brute Force | 430,281 |
| Database Attack | 277,202 |
| Telnet Attack | 194,055 |
| DNS Attack | 128,538 |
| SMB Attack | 81,510 |
| FTP Attack | 31,248 |
| Email Attack | 10,869 |

### K-Means Clustering — Campaign Detection
Groups attacks with similar behavioral patterns to identify
coordinated botnet campaigns and repeated attacker strategies.
8 clusters including SSH Brute Force, SMB, and Web Exploit campaigns.

### LSTM Neural Network — Attack Prediction
Learns temporal attack sequences to predict the next likely
attack type. Uses last 10 attacks as input, outputs probability
distribution across all 9 attack classes with confidence score.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API info |
| GET | `/health` | System health |
| POST | `/analyze` | Analyze attack through ML |
| GET | `/attacks` | Recent attacks |
| GET | `/stats` | Aggregated statistics |
| GET | `/live` | SSE real-time stream |
| GET | `/mitre/heatmap` | ATT&CK tactic frequency |
| GET | `/mitre/detail/{type}` | Full MITRE entry |
| GET | `/investigations` | TI agent reports |
| POST | `/investigate` | Trigger TI investigation |
| GET | `/predict/next` | LSTM prediction |
| POST | `/predict/train` | Retrain LSTM |
| GET | `/stats/geographic` | Hornet 40 geo stats |
| GET | `/report/html` | Visual HTML report |
| GET | `/report/generate` | Download PDF report |
| DELETE | `/attacks/clear` | Reset store |

**Interactive docs:** http://localhost:8000/docs

---

## 📁 Project Structure
```
HoneyCloud-Sentinel/
│
├── api/
│   ├── threat_api.py           # FastAPI — all 16 endpoints
│   └── attack_store.py         # Thread-safe attack store
│
├── honeypots/
│   └── ssh_honeypot.py         # SSH decoy service
│
├── data_pipeline/
│   ├── kafka_producer.py
│   └── kafka_consumer.py
│
├── ml_models/
│   ├── feature_engineering.py  # 7-feature extractor
│   ├── anomaly_detection.py    # Isolation Forest
│   ├── attack_classifier.py    # Random Forest (9 classes)
│   ├── clustering.py           # K-Means (8 clusters)
│   ├── risk_scorer.py          # 0-100 risk scoring
│   └── attack_predictor.py     # LSTM prediction
│
├── ai_agents/
│   ├── mitre_mapper.py         # MITRE ATT&CK mapping
│   ├── threat_intelligence_agent.py  # 4-agent pipeline
│   ├── threat_report_agent.py  # Groq LLM writer
│   ├── html_report_generator.py
│   └── pdf_generator.py
│
├── dashboard/                  # Next.js 14 frontend
│   ├── app/
│   │   ├── page.tsx            # Main dashboard
│   │   └── globals.css         # Dark SOC theme
│   └── components/
│       ├── Header.tsx
│       ├── StatCards.tsx
│       ├── AttackMap.tsx       # Leaflet world map
│       ├── GlobalHoneypotNetwork.tsx
│       ├── Charts.tsx
│       ├── MitreHeatmap.tsx
│       ├── PredictionPanel.tsx
│       ├── InvestigationPanel.tsx
│       ├── AttackFeed.tsx
│       └── ReportButton.tsx
│
├── scripts/
│   ├── demo.py                 # 5-phase attack demo
│   ├── train_all_models.py     # Train RF + IF + KMeans
│   ├── train_lstm.py           # Train LSTM
│   ├── extract_pcap_test.py    # CIC Phase 2.1
│   ├── extract_pcap_full.py    # CIC Phase 2.2
│   ├── merge_datasets.py       # AWS + Dionaea merge
│   ├── merge_with_cic.py       # Add CIC test data
│   └── merge_cic_full.py       # Final dataset merge
│
├── datasets/
│   └── README.md               # Download links
│
├── docs/
│   └── screenshots/            # Dashboard screenshots
│
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🎬 Demo
```bash
python scripts/demo.py          # Full 5-phase demo (~3 min)
python scripts/demo.py --quick  # Quick 30-second demo
```

| Phase | What Happens | Time |
|---|---|---|
| 0 | Background internet noise — LOW risk baseline | 15s |
| 1 | Initial reconnaissance — slow port scans | 15s |
| 2 | Botnet campaign — 20 coordinated IPs | 10s |
| 3 | APT scenario — same IP, multiple vectors | 20s |
| 4 | Mass attack flood — 40 rapid mixed attacks | 8s |
| 5 | Critical DB breach — 3 simultaneous hits | 5s |

Reset between runs:
```bash
curl -X DELETE http://localhost:8000/attacks/clear
```

---

## 🔐 Ethical Considerations

- Honeypots only simulate vulnerable environments
- No real user data is exposed
- Malware isolated in sandboxed environments
- Attack data anonymized before sharing
- No offensive actions taken against attackers
- Complies with responsible cybersecurity research

---

## 🔮 Future Work

1. **T-Pot Integration** — connect to real cloud honeypot platform
2. **Global Honeypot Network** — deploy across multiple cloud regions
3. **CERT-In Integration** — share threat signatures nationally
4. **Full MITRE Coverage** — all 14 ATT&CK tactic categories
5. **Automated Defense** — auto-update firewall rules from detections

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Honeypots | Python sockets, T-Pot |
| Streaming | Apache Kafka 3.0 |
| Backend | Python 3.10, FastAPI |
| ML | Scikit-learn, TensorFlow, XGBoost |
| AI Pipeline | Groq API, Llama 3.3 70B (free) |
| Frontend | Next.js 14, Tailwind, shadcn/ui |
| Visualization | Recharts, Leaflet |
| Reports | ReportLab, HTML/CSS |
| DevOps | Docker, Docker Compose |
| Threat Intel | MITRE ATT&CK, ip-api.com |

---

<div align="center">

**HoneyCloud Sentinel**

*Transforming attacker behavior into actionable cyber intelligence.*

⭐ Star this repo if you found it useful

</div>