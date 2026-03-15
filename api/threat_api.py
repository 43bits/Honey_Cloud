# # api/threat_api.py

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel
# from typing import Optional
# import json
# import asyncio
# import time

# from api.attack_store import store
# from ml_models.feature_engineering import engineer_features_from_live_log
# from ml_models.anomaly_detection import predict_anomaly
# from ml_models.attack_classifier import predict_attack_type
# from ml_models.clustering import predict_cluster
# from ml_models.risk_scorer import calculate_risk_score


# # ── App Setup ──────────────────────────────────────────

# app = FastAPI(
#     title="HoneyCloud Sentinel API",
#     description="AI-powered honeypot threat detection",
#     version="1.0.0"
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ── Request Model ──────────────────────────────────────

# class AttackLog(BaseModel):
#     source_ip: str
#     source_port: Optional[int] = 0
#     port_targeted: Optional[int] = 22
#     protocol: Optional[str] = "tcp"
#     timestamp: Optional[str] = None
#     country: Optional[str] = "Unknown"
#     login_attempts: Optional[int] = 1
#     connection_rate: Optional[float] = 1.0
#     data_hex: Optional[str] = ""


# # ── ML PIPELINE ───────────────────────────────────────

# def run_ml_pipeline(log: dict) -> dict:
#     """Run all ML models and return JSON-safe result"""

#     features = engineer_features_from_live_log(log)
#     dst_port = log.get("port_targeted", 22)

#     # Run models
#     is_anomaly, anomaly_score = predict_anomaly(features)
#     attack_type, confidence = predict_attack_type(features)
#     campaign = predict_cluster(features)

#     risk_score, risk_level, emoji = calculate_risk_score(
#         attack_type,
#         confidence,
#         is_anomaly,
#         anomaly_score,
#         dst_port,
#         campaign
#     )

#     # 🔥 Convert ALL ML outputs to JSON-safe types
#     return {
#         **log,
#         "attack_type": str(attack_type),
#         "confidence": float(confidence),
#         "is_anomaly": bool(is_anomaly),
#         "anomaly_score": float(anomaly_score),
#         "campaign": str(campaign),
#         "risk_score": int(risk_score),
#         "risk_level": str(risk_level),
#         "emoji": str(emoji),
#         "timestamp": log.get(
#             "timestamp",
#             time.strftime("%Y-%m-%d %H:%M:%S")
#         )
#     }


# # ── Routes ─────────────────────────────────────────────

# @app.get("/")
# def root():
#     return {
#         "name": "HoneyCloud Sentinel API",
#         "status": "running",
#         "endpoints": ["/analyze", "/attacks", "/stats", "/risk", "/live", "/health"]
#     }


# @app.get("/health")
# def health():
#     return {"status": "ok", "total_attacks_recorded": store.get_stats()["total_attacks"]}


# @app.post("/analyze")
# def analyze(log: AttackLog):
#     """
#     Analyze a single attack log through ML models
#     """
#     result = run_ml_pipeline(log.dict())

#     store.add(result)

#     return result


# @app.get("/attacks")
# def get_attacks(limit: int = 50):
#     limit = min(limit, 200)

#     attacks = store.get_recent(limit)

#     return {
#         "attacks": attacks,
#         "count": len(attacks)
#     }


# @app.get("/stats")
# def get_stats():
#     return store.get_stats()


# @app.get("/risk")
# def get_risk_breakdown():

#     stats = store.get_stats()
#     risk = stats["by_risk"]
#     total = stats["total_attacks"] or 1

#     return {
#         "counts": risk,
#         "percentages": {
#             k: round(v / total * 100, 1)
#             for k, v in risk.items()
#         },
#         "highest_risk": max(
#             risk,
#             key=lambda k: {"LOW":1,"MEDIUM":2,"HIGH":3,"CRITICAL":4}[k]
#             if risk[k] > 0 else 0
#         )
#     }


# @app.get("/live")
# async def live_stream():

#     async def event_generator():
#         last_count = 0

#         while True:

#             current = store.get_recent(1)
#             stats = store.get_stats()

#             current_count = stats["total_attacks"]

#             if current_count != last_count and current:

#                 latest = current[0]
#                 data = json.dumps(latest)

#                 yield f"data: {data}\n\n"

#                 last_count = current_count

#             await asyncio.sleep(1)

#     return StreamingResponse(
#         event_generator(),
#         media_type="text/event-stream",
#         headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
#     )


# @app.delete("/attacks/clear")
# def clear_attacks():

#     store.clear()

#     return {"message": "Attack store cleared"}

# api/threat_api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio
import time
import threading
import urllib.request

from api.attack_store import store
from ml_models.feature_engineering import engineer_features_from_live_log
from ml_models.anomaly_detection import predict_anomaly
from ml_models.attack_classifier import predict_attack_type
from ml_models.clustering import predict_cluster
from ml_models.risk_scorer import calculate_risk_score

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


# Add this helper function
def get_ip_location(ip: str) -> dict:
    """Get lat/lon for an IP using free ip-api.com service."""
    try:
        # Skip private/local IPs
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
    except:
        pass
    return {'lat': 0, 'lon': 0, 'country': 'Unknown', 'city': 'Unknown'}

# ── ML Pipeline Helper ─────────────────────────────────
def run_ml_pipeline(log: dict) -> dict:
    features  = engineer_features_from_live_log(log)
    dst_port  = log.get('port_targeted', 22)

    is_anomaly, anomaly_score = predict_anomaly(features)
    attack_type, confidence   = predict_attack_type(features)
    campaign                  = predict_cluster(features)
    risk_score, risk_level, emoji = calculate_risk_score(
        attack_type, confidence, is_anomaly, anomaly_score, dst_port, campaign
    )

    # Get geo location for the source IP
    geo = get_ip_location(log.get('source_ip', ''))

    return {
        **log,
        'attack_type':   str(attack_type),
        'confidence':    float(confidence),
        'is_anomaly':    bool(is_anomaly),
        'anomaly_score': float(anomaly_score),
        'campaign':      str(campaign),
        'risk_score':    int(risk_score),
        'risk_level':    str(risk_level),
        'emoji':         str(emoji),
        'timestamp':     log.get('timestamp', time.strftime('%Y-%m-%d %H:%M:%S')),
        # Geo fields
        'lat':           geo['lat'],
        'lon':           geo['lon'],
        'country':       geo.get('country', log.get('country', 'Unknown')),
        'city':          geo.get('city', 'Unknown'),
    }
    
# ── Kafka Consumer Thread ──────────────────────────────
# This runs INSIDE the API process so it shares the same store
def kafka_consumer_thread():
    """Runs as a background thread inside the API process."""
    import time as t
    # Wait a moment for API to fully start
    t.sleep(3)

    try:
        from kafka import KafkaConsumer
        consumer = KafkaConsumer(
            'honeypot-attacks',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='honeypot-api-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=-1   # never stop
        )
        print("\n[✓] Kafka consumer started inside API — sharing same store")

        for message in consumer:
            log = message.value
            result = run_ml_pipeline(log)
            store.add(result)   # ← same store the API reads from!
            print(f"[Kafka] {result['emoji']} {result['attack_type']} from {result['source_ip']}")

    except Exception as e:
        print(f"[!] Kafka consumer thread error: {e}")
        print("[!] API will still work — use /analyze endpoint directly")


# ── Start Kafka thread when API starts ─────────────────
@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
    thread.start()
    print("[✓] HoneyCloud Sentinel API started")
    print("[✓] Kafka consumer thread launched")


# ── All your existing routes below (unchanged) ─────────

class AttackLog(BaseModel):
    source_ip: str
    source_port: Optional[int] = 0
    port_targeted: Optional[int] = 22
    protocol: Optional[str] = "tcp"
    timestamp: Optional[str] = None
    country: Optional[str] = "Unknown"
    login_attempts: Optional[int] = 1
    connection_rate: Optional[float] = 1.0
    data_hex: Optional[str] = ""

@app.get("/")
def root():
    return {"name": "HoneyCloud Sentinel API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok", "total_attacks_recorded": store.get_stats()['total_attacks']}

@app.post("/analyze")
def analyze(log: AttackLog):
    result = run_ml_pipeline(log.dict())
    store.add(result)
    return result

@app.get("/attacks")
def get_attacks(limit: int = 50):
    limit = min(limit, 200)
    return {"attacks": store.get_recent(limit), "count": len(store.get_recent(limit))}

@app.get("/stats")
def get_stats():
    return store.get_stats()

@app.get("/risk")
def get_risk_breakdown():
    stats = store.get_stats()
    risk = stats['by_risk']
    total = stats['total_attacks'] or 1
    return {
        "counts": risk,
        "percentages": {k: round(v / total * 100, 1) for k, v in risk.items()},
        "highest_risk": max(risk, key=lambda k: {'LOW':1,'MEDIUM':2,'HIGH':3,'CRITICAL':4}[k] if risk[k] > 0 else 0)
    }

@app.get("/live")
async def live_stream():
    async def event_generator():
        last_count = 0
        while True:
            current = store.get_recent(1)
            stats = store.get_stats()
            current_count = stats['total_attacks']
            if current_count != last_count and current:
                yield f"data: {json.dumps(current[0])}\n\n"
                last_count = current_count
            await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.delete("/attacks/clear")
def clear_attacks():
    store.clear()
    return {"message": "Attack store cleared"}