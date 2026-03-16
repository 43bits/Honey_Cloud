# scripts/diagnose.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 50)
print("  HoneyCloud Diagnostic")
print("=" * 50)

# ── Check 1: Model files exist ─────────────────────
print("\n[1] Checking model files...")
import os
models = [
    'models/anomaly_detector.pkl',
    'models/attack_classifier.pkl',
    'models/attack_labels.pkl',
    'models/attack_index_map.pkl',
    'models/clustering.pkl',
    'models/cluster_scaler.pkl',
    'models/cluster_names.pkl',
]
all_good = True
for m in models:
    exists = os.path.exists(m)
    status = '✓' if exists else '✗ MISSING'
    print(f"   {status}  {m}")
    if not exists:
        all_good = False

if not all_good:
    print("\n[!] Missing models — run: python scripts/train_all_models.py")

# ── Check 2: Load models ───────────────────────────
print("\n[2] Loading models...")
try:
    import joblib
    clf    = joblib.load('models/attack_classifier.pkl')
    labels = joblib.load('models/attack_labels.pkl')
    imap   = joblib.load('models/attack_index_map.pkl')
    print(f"   ✓ Classifier loaded")
    print(f"   ✓ Labels type: {type(labels)}")
    print(f"   ✓ Labels content: {labels}")
    print(f"   ✓ Index map: {imap}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# ── Check 3: Feature engineering ──────────────────
print("\n[3] Testing feature engineering...")
try:
    from ml_models.feature_engineering import engineer_features_from_live_log
    test_log = {
        'source_ip':     '185.234.219.4',
        'source_port':   54321,
        'port_targeted': 22,
        'protocol':      'tcp',
        'country':       'Russia',
    }
    features = engineer_features_from_live_log(test_log)
    print(f"   ✓ Features: {features}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# ── Check 4: Anomaly detection ─────────────────────
print("\n[4] Testing anomaly detection...")
try:
    from ml_models.anomaly_detection import predict_anomaly
    is_anomaly, score = predict_anomaly(features)
    print(f"   ✓ is_anomaly={is_anomaly}, score={score}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# ── Check 5: Attack classifier ─────────────────────
print("\n[5] Testing attack classifier...")
try:
    from ml_models.attack_classifier import predict_attack_type
    attack_type, confidence = predict_attack_type(features)
    print(f"   ✓ attack_type={attack_type}, confidence={confidence}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# ── Check 6: Clustering ────────────────────────────
print("\n[6] Testing clustering...")
try:
    from ml_models.clustering import predict_cluster
    campaign = predict_cluster(features)
    print(f"   ✓ campaign={campaign}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# ── Check 7: Full pipeline ─────────────────────────
print("\n[7] Testing full ML pipeline...")
try:
    from ml_models.risk_scorer import calculate_risk_score
    import numpy as np
    risk_score, risk_level, emoji = calculate_risk_score(
        str(attack_type), float(confidence),
        bool(is_anomaly), float(score),
        22, str(campaign)
    )
    print(f"   ✓ risk_score={risk_score}, level={risk_level}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# ── Check 8: Kafka connection ──────────────────────
print("\n[8] Testing Kafka connection...")
try:
    from kafka import KafkaProducer
    import json
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )
    producer.send('honeypot-attacks', {'test': True})
    producer.flush()
    producer.close()
    print("   ✓ Kafka connection OK")
except Exception as e:
    print(f"   ✗ Kafka ERROR: {e}")

print("\n" + "=" * 50)
print("  Diagnostic complete")
print("=" * 50)
