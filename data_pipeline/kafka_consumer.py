# data_pipeline/kafka_consumer.py
from kafka import KafkaConsumer
import json
import sys
import os

# Make sure Python finds our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.attack_store import store
from ml_models.feature_engineering import engineer_features_from_live_log
from ml_models.anomaly_detection import predict_anomaly
from ml_models.attack_classifier import predict_attack_type
from ml_models.clustering import predict_cluster
from ml_models.risk_scorer import calculate_risk_score
import time


def analyze_attack(log):
    features = engineer_features_from_live_log(log)
    dst_port = log.get('port_targeted', 22)

    is_anomaly, anomaly_score = predict_anomaly(features)
    attack_type, confidence = predict_attack_type(features)
    campaign = predict_cluster(features)
    risk_score, risk_level, emoji = calculate_risk_score(
        attack_type, confidence, is_anomaly,
        anomaly_score, dst_port, campaign
    )

    return {
        **log,
        'attack_type':  attack_type,
        'confidence':   confidence,
        'is_anomaly':   is_anomaly,
        'campaign':     campaign,
        'risk_score':   risk_score,
        'risk_level':   risk_level,
        'emoji':        emoji,
        'timestamp':    log.get('timestamp', time.strftime('%Y-%m-%d %H:%M:%S'))
    }


def print_threat_report(result):
    print("\n" + "─" * 50)
    print(f"  {result['emoji']}  {result['risk_level']} THREAT DETECTED")
    print("─" * 50)
    print(f"  IP          : {result['source_ip']}")
    print(f"  Port        : {result['port_targeted']}")
    print(f"  Attack Type : {result['attack_type']} ({result['confidence']}%)")
    print(f"  Anomaly     : {'YES ⚠️' if result['is_anomaly'] else 'No'}")
    print(f"  Campaign    : {result['campaign']}")
    print(f"  Risk Score  : {result['risk_score']}/100")
    print("─" * 50)


def start_consumer():
    consumer = KafkaConsumer(
        'honeypot-attacks',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='honeypot-ml-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print('\n[*] HoneyCloud ML Consumer + API Store running...\n')

    for message in consumer:
        log = message.value
        result = analyze_attack(log)
        store.add(result)           # ← saves to API store
        print_threat_report(result)


if __name__ == '__main__':
    start_consumer()
    
# from kafka import KafkaConsumer
# import json
# import sys
# import os
# import time

# # Ensure modules are found
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from api.attack_store import store
# from ml_models.feature_engineering import engineer_features_from_live_log
# from ml_models.anomaly_detection import predict_anomaly
# from ml_models.attack_classifier import predict_attack_type
# from ml_models.clustering import predict_cluster
# from ml_models.risk_scorer import calculate_risk_score


# def analyze_attack(log):
#     """Run ML pipeline and convert all values to JSON-safe types."""
#     features = engineer_features_from_live_log(log)
#     dst_port = log.get("port_targeted", 22)

#     # Run ML models
#     is_anomaly, anomaly_score = predict_anomaly(features)
#     attack_type, confidence = predict_attack_type(features)
#     campaign = predict_cluster(features)
#     risk_score, risk_level, emoji = calculate_risk_score(
#         attack_type, confidence, is_anomaly,
#         anomaly_score, dst_port, campaign
#     )

#     # Return JSON-safe dict
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
#         "timestamp": log.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
#     }


# def print_threat_report(result):
#     print("\n" + "─" * 50)
#     print(f"  {result['emoji']}  {result['risk_level']} THREAT DETECTED")
#     print("─" * 50)
#     print(f"  IP          : {result.get('source_ip')}")
#     print(f"  Port        : {result.get('port_targeted', result.get('port'))}")
#     print(f"  Attack Type : {result['attack_type']} ({result['confidence']}%)")
#     print(f"  Anomaly     : {'YES ⚠️' if result['is_anomaly'] else 'No'}")
#     print(f"  Campaign    : {result['campaign']}")
#     print(f"  Risk Score  : {result['risk_score']}/100")
#     print("─" * 50)


# def start_consumer():
#     consumer = KafkaConsumer(
#         'honeypot-attacks',
#         bootstrap_servers=['localhost:9092'],
#         auto_offset_reset='earliest',   # ← detect all test attacks
#         enable_auto_commit=True,
#         group_id='honeypot-ml-group',
#         value_deserializer=lambda m: json.loads(m.decode('utf-8'))
#     )

#     print('\n[*] HoneyCloud ML Consumer + API Store running...\n')

#     for message in consumer:
#         log = message.value

#         # Ensure correct fields for ML
#         log.setdefault('protocol', 'tcp')
#         log.setdefault('port_targeted', 22)
#         log.setdefault('source_port', 0)

#         result = analyze_attack(log)
#         store.add(result)
#         print_threat_report(result)


# if __name__ == '__main__':
#     start_consumer()