# api/threat_api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import json
import asyncio
import time
import threading
import urllib.request
import pandas as pd

from api.attack_store import store, investigation_store
from ml_models.feature_engineering import engineer_features_from_live_log
from ml_models.anomaly_detection import predict_anomaly
from ml_models.attack_classifier import predict_attack_type
from ml_models.clustering import predict_cluster
from ml_models.risk_scorer import calculate_risk_score

load_dotenv()

# ── App Setup ──────────────────────────────────────────
app = FastAPI(
    title="HoneyCloud Sentinel API",
    description="AI-powered honeypot threat detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request Model ──────────────────────────────────────
class AttackLog(BaseModel):
    source_ip:       str
    source_port:     Optional[int]   = 0
    port_targeted:   Optional[int]   = 22
    protocol:        Optional[str]   = "tcp"
    timestamp:       Optional[str]   = None
    country:         Optional[str]   = "Unknown"
    login_attempts:  Optional[int]   = 1
    connection_rate: Optional[float] = 1.0
    data_hex:        Optional[str]   = ""




# ── ML Pipeline ────────────────────────────────────────
def run_ml_pipeline(log: dict) -> dict:
    """Run all ML models + MITRE mapping on a raw log dict."""

    features = engineer_features_from_live_log(log)
    dst_port = log.get('port_targeted', 22)

    is_anomaly,  anomaly_score = predict_anomaly(features)
    attack_type, confidence    = predict_attack_type(features)
    campaign                   = predict_cluster(features)
    # risk_score, risk_level, emoji = calculate_risk_score(
    #     attack_type, confidence, is_anomaly,
    #     anomaly_score, dst_port, campaign
    # )
    risk_score, risk_level, emoji = calculate_risk_score(
        attack_type,
        confidence,
        is_anomaly,
        anomaly_score,
        dst_port,
        campaign,
        login_attempts  = int(log.get('login_attempts',  1) or 1),
        connection_rate = float(log.get('connection_rate', 1.0) or 1.0),
    )

    geo   = get_ip_location(log.get('source_ip', ''))

    from ai_agents.mitre_mapper import map_attack_to_mitre
    mitre = map_attack_to_mitre(str(attack_type))

    result = {
        **log,
        'attack_type':          str(attack_type),
        'confidence':           float(confidence),
        'is_anomaly':           bool(is_anomaly),
        'anomaly_score':        float(anomaly_score),
        'campaign':             str(campaign),
        'risk_score':           int(risk_score),
        'risk_level':           str(risk_level),
        'emoji':                str(emoji),
        'timestamp':            log.get(
                                    'timestamp',
                                    time.strftime('%Y-%m-%d %H:%M:%S')
                                ),
        # Geo
        'lat':                  geo['lat'],
        'lon':                  geo['lon'],
        'country':              geo.get('country', log.get('country', 'Unknown')),
        'city':                 geo.get('city', 'Unknown'),
        # MITRE
        'mitre_technique_id':   mitre['technique_id'],
        'mitre_technique_name': mitre['technique_name'],
        'mitre_tactic':         mitre['tactic'],
        'mitre_tactic_id':      mitre['tactic_id'],
        'mitre_url':            mitre['url'],
        'mitre_mapped':         mitre['mitre_mapped'],
    }

    # Auto-trigger TI investigation for HIGH/CRITICAL
    # if result.get('risk_level') in ('HIGH', 'CRITICAL'):
    #     trigger_investigation(result)

    return result


# ── TI Investigation ───────────────────────────────────
def trigger_investigation(attack: dict):
    """
    Runs TI agent pipeline in a background thread.
    Non-blocking — does not slow down the API response.
    """
    def _run():
        try:
            from ai_agents.threat_intelligence_agent import (
                run_threat_intelligence_pipeline
            )
            report = run_threat_intelligence_pipeline(attack)
            if not report.get('skipped'):
                investigation_store.add(attack, report)
                print(
                    f"[TI] Investigation stored for "
                    f"{attack.get('source_ip', '?')}"
                )
        except Exception as e:
            print(f"[TI] Investigation failed: {e}")

    threading.Thread(target=_run, daemon=True).start()
    


# ── Geo Location Helper ────────────────────────────────
def get_ip_location(ip: str) -> dict:
    """Get lat/lon for an IP using free ip-api.com service."""
    try:
        if ip.startswith(('192.168.', '10.', '172.', '127.', 'localhost')):
            return {'lat': 0, 'lon': 0, 'country': 'Local', 'city': 'Local'}

        url = f'http://ip-api.com/json/{ip}?fields=lat,lon,country,city,status'
        with urllib.request.urlopen(url, timeout=2) as response:
            data = json.loads(response.read())
            if data.get('status') == 'success':
                return {
                    'lat':     float(data.get('lat', 0)),
                    'lon':     float(data.get('lon', 0)),
                    'country': str(data.get('country', 'Unknown')),
                    'city':    str(data.get('city', 'Unknown')),
                }
    except Exception:
        pass
    return {'lat': 0, 'lon': 0, 'country': 'Unknown', 'city': 'Unknown'}



# ── Kafka Consumer Thread ──────────────────────────────
def kafka_consumer_thread():
    """
    Runs inside the API process so it shares the same
    attack_store and investigation_store as the API.
    """
    time.sleep(3)  # wait for API to fully start

    try:
        from kafka import KafkaConsumer
        consumer = KafkaConsumer(
            'honeypot-attacks',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            # group_id='honeypot-api-group',
            group_id=f'honeypot-api-{int(time.time())}',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=-1
        )
        print("\n[✓] Kafka consumer started inside API — sharing same store")

        for message in consumer:
            log    = message.value
            result = run_ml_pipeline(log)
            store.add(result)
            print(
                f"[Kafka] {result['emoji']} "
                f"{result['attack_type']} from "
                f"{result['source_ip']}"
            )

    except Exception as e:
        print(f"[!] Kafka consumer thread error: {e}")
        print("[!] API still works — use /analyze endpoint directly")


# ── Startup ────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    threading.Thread(
        target=kafka_consumer_thread, daemon=True
    ).start()
    print("[✓] HoneyCloud Sentinel API started")
    print("[✓] Kafka consumer thread launched")


# ══════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════

# ── Core ───────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "name":      "HoneyCloud Sentinel API",
        "status":    "running",
        "version":   "1.0.0",
        "endpoints": [
            "/analyze", "/attacks", "/stats", "/risk",
            "/live", "/health", "/mitre/heatmap",
            "/investigations", "/report/html",
            "/report/generate",
        ]
    }


@app.get("/health")
def health():
    return {
        "status":                 "ok",
        "total_attacks_recorded": store.get_stats()['total_attacks'],
        "total_investigations":   investigation_store.count(),
    }


# ── Attack Analysis ────────────────────────────────────
@app.post("/analyze")
def analyze(log: AttackLog):
    """Analyze a single attack through all ML models."""
    result = run_ml_pipeline(log.dict())
    store.add(result)
    return result


@app.get("/attacks")
def get_attacks(limit: int = 50):
    """Get most recent attacks, newest first."""
    limit   = min(limit, 200)
    attacks = store.get_recent(limit)
    return {"attacks": attacks, "count": len(attacks)}


@app.get("/stats")
def get_stats():
    """Get aggregated attack statistics."""
    return store.get_stats()


@app.get("/risk")
def get_risk_breakdown():
    """Get risk level counts and percentages."""
    stats = store.get_stats()
    risk  = stats['by_risk']
    total = stats['total_attacks'] or 1
    return {
        "counts": risk,
        "percentages": {
            k: round(v / total * 100, 1)
            for k, v in risk.items()
        },
        "highest_risk": max(
            risk,
            key=lambda k: (
                {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}[k]
                if risk[k] > 0 else 0
            )
        )
    }


@app.delete("/attacks/clear")
def clear_attacks():
    """Clear all stored attacks — useful for demo resets."""
    store.clear()
    return {"message": "Attack store cleared"}


# ── Live Stream ────────────────────────────────────────
@app.get("/live")
async def live_stream():
    """Server-Sent Events stream for real-time dashboard updates."""
    async def event_generator():
        last_count = 0
        while True:
            current       = store.get_recent(1)
            stats         = store.get_stats()
            current_count = stats['total_attacks']
            if current_count != last_count and current:
                yield f"data: {json.dumps(current[0])}\n\n"
                last_count = current_count
            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering":"no",
        }
    )







# ── MITRE ATT&CK ──────────────────────────────────────
@app.get("/mitre/heatmap")
def mitre_heatmap():
    """Returns tactic frequency data for the ATT&CK heatmap."""
    from ai_agents.mitre_mapper import build_heatmap_data
    attacks = store.get_recent(200)
    return {
        'heatmap':       build_heatmap_data(attacks),
        'total_mapped':  sum(
            1 for a in attacks if a.get('mitre_mapped', False)
        ),
        'total_attacks': len(attacks),
    }


@app.get("/mitre/detail/{attack_type}")
def mitre_detail(attack_type: str):
    """Returns full MITRE entry for a specific attack type."""
    from ai_agents.mitre_mapper import get_mitre_detail
    detail = get_mitre_detail(attack_type)
    if not detail:
        return {"error": f"No MITRE mapping for: {attack_type}"}
    return detail




# ── Threat Intelligence Agent ──────────────────────────
@app.get("/investigations")
def get_investigations(limit: int = 10):
    """Get recent TI agent investigation reports."""
    return {
        "investigations": investigation_store.get_recent(limit),
        "total":          investigation_store.count(),
    }


# @app.post("/investigate")
# def investigate_attack(log: AttackLog):
#     from ai_agents.threat_intelligence_agent import (
#         run_threat_intelligence_pipeline
#     )
#     result = run_ml_pipeline(log.dict())
#     # force=True — manual investigations always run
#     # regardless of calculated risk level
#     report = run_threat_intelligence_pipeline(result, force=True)

#     if not report.get('skipped'):
#         investigation_store.add(result, report)

#     return {"attack": result, "investigation": report}

@app.post("/investigate")
def investigate_attack(log: AttackLog):
    """
    Manually trigger a TI investigation.
    Always runs regardless of risk level (force=True).
    """
    from ai_agents.threat_intelligence_agent import (
        run_threat_intelligence_pipeline
    )
    result = run_ml_pipeline(log.dict())

    # force=True — manual investigations always run
    report = run_threat_intelligence_pipeline(result, force=True)

    if not report.get('skipped'):
        investigation_store.add(result, report)

    return {"attack": result, "investigation": report}


# ── Reports ────────────────────────────────────────────
@app.get("/report/html")
def report_html():
    """Returns full visual HTML report — opens in browser."""
    from ai_agents.threat_report_agent   import generate_threat_report
    from ai_agents.html_report_generator import generate_html_report

    attacks = store.get_recent(100)
    stats   = store.get_stats()

    if stats['total_attacks'] == 0:
        return Response(
            content=(
                "<div style='color:#00ffe7;font-family:monospace;"
                "background:#080c14;padding:40px;font-size:18px'>"
                "No attack data yet. Run the demo first."
                "</div>"
            ),
            media_type="text/html"
        )

    report_text = generate_threat_report(stats, attacks)
    html        = generate_html_report(report_text, stats, attacks)
    return Response(content=html, media_type="text/html")


@app.get("/report/generate")
def generate_report():
    """Returns dark-themed PDF — triggers browser download."""
    from ai_agents.threat_report_agent import generate_threat_report
    from ai_agents.pdf_generator       import generate_pdf

    attacks = store.get_recent(100)
    stats   = store.get_stats()

    if stats['total_attacks'] == 0:
        return {"error": "No attack data yet. Run the demo first."}

    report_text = generate_threat_report(stats, attacks)
    pdf_bytes   = generate_pdf(report_text, stats, attacks)

    filename = (
        f"HoneyCloud_Report_"
        f"{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
    
    
    
    
# model predictionEngine api/threat_api.py

@app.get("/predict/next")
def predict_next():
    """
    Predicts the next likely attack based on recent sequence.
    Uses LSTM model trained on attack patterns.
    """
    from ml_models.PredictionEngine.attack_predictor import (
        predict_next_attack,
        get_recommendation,
    )

    # Get recent attack types as sequence
    recent  = store.get_recent(20)
    types   = [a.get('attack_type', 'Port Scan / Other')
               for a in recent]

    if len(types) < 3:
        return {
            'ready':      False,
            'reason':     'Need at least 3 attacks to predict',
            'predicted':  None,
            'confidence': 0,
        }

    result = predict_next_attack(types)

    if result.get('ready'):
        result['recommendation'] = get_recommendation(
            result['predicted'],
            result['confidence'],
        )

    return result


@app.post("/predict/train")
def retrain_model():
    """
    Retrain LSTM on current stored attack data.
    Call this after collecting enough real attacks.
    """
    from ml_models.PredictionEngine.attack_predictor import train_lstm

    attacks = store.get_recent(200)
    types   = [
        a.get('attack_type', 'Port Scan / Other')
        for a in attacks
    ]

    if len(types) < 20:
        return {
            "error": f"Need 20+ attacks to train. Have {len(types)}."
        }

    threading.Thread(
        target=train_lstm,
        args=(types,),
        daemon=True,
    ).start()

    return {
        "message": f"Training started on {len(types)} attacks",
        "status":  "running in background",
    }
    
    
# Add to api/threat_api.py

# @app.get("/stats/geographic")
# def geographic_stats():
#     """
#     Returns Hornet 40 geographic attack volume data.
#     Shows which global regions are most targeted.
#     """
#     import os
#     hornet_path = 'datasets/hornet40_processed.csv'

#     if not os.path.exists(hornet_path):
#         return {"error": "Hornet 40 data not processed yet"}

#     df = pd.read_csv(hornet_path)

#     # Total attacks per city across all 40 days
#     city_totals = df.groupby('city')['attack_count']\
#         .sum().sort_values(ascending=False)

#     # Peak hour per city
#     peak_hours = df.groupby(['city', 'hour'])['attack_count']\
#         .sum().reset_index()
#     peak_per_city = peak_hours.loc[
#         peak_hours.groupby('city')['attack_count'].idxmax()
#     ][['city', 'hour']].set_index('city')['hour'].to_dict()

#     # Busiest day of week globally
#     day_totals = df.groupby('weekday')['attack_count']\
#         .sum().sort_values(ascending=False)

#     return {
#         "source":        "Hornet 40 Dataset — 40 days, 8 global locations",
#         "city_totals":   city_totals.to_dict(),
#         "peak_hours":    peak_per_city,
#         "busiest_days":  day_totals.head(3).to_dict(),
#         "total_events":  int(city_totals.sum()),
#     }
    
    



