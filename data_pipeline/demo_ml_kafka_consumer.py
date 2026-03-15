# data_pipeline/kafka_consumer.py
from kafka import KafkaConsumer
import json

from ml_models.feature_engineering import engineer_features_from_live_log
from ml_models.anomaly_detection import predict_anomaly
from ml_models.attack_classifier import predict_attack_type
from ml_models.clustering import predict_cluster
from ml_models.risk_scorer import calculate_risk_score


def analyze_attack(log):
    """Run all ML models on a single attack log."""

    # Step 1: Extract features
    features = engineer_features_from_live_log(log)
    dst_port = log.get('port_targeted', 22)

    # Step 2: Anomaly detection
    is_anomaly, anomaly_score = predict_anomaly(features)

    # Step 3: Attack classification
    attack_type, confidence = predict_attack_type(features)

    # Step 4: Campaign clustering
    campaign = predict_cluster(features)

    # Step 5: Risk scoring
    risk_score, risk_level, emoji = calculate_risk_score(
        attack_type, confidence, is_anomaly,
        anomaly_score, dst_port, campaign
    )

    return {
        'source_ip':    log.get('source_ip', 'unknown'),
        'timestamp':    log.get('timestamp', 'unknown'),
        'port':         dst_port,
        'attack_type':  attack_type,
        'confidence':   confidence,
        'is_anomaly':   is_anomaly,
        'campaign':     campaign,
        'risk_score':   risk_score,
        'risk_level':   risk_level,
        'emoji':        emoji
    }


def print_threat_report(result):
    """Print a clean threat report to the terminal."""
    print("\n" + "─" * 50)
    print(f"  {result['emoji']}  THREAT DETECTED  {result['emoji']}")
    print("─" * 50)
    print(f"  IP Address  : {result['source_ip']}")
    print(f"  Port        : {result['port']}")
    print(f"  Attack Type : {result['attack_type']} ({result['confidence']}% confidence)")
    print(f"  Anomaly     : {'YES ⚠️' if result['is_anomaly'] else 'No'}")
    print(f"  Campaign    : {result['campaign']}")
    print(f"  Risk Level  : {result['risk_level']} (score: {result['risk_score']}/100)")
    print(f"  Time        : {result['timestamp']}")
    print("─" * 50)


def start_consumer():
    consumer = KafkaConsumer(
        'honeypot-attacks',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='honeypot-ml-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print('\n[*] HoneyCloud ML Consumer started.')
    print('[*] Waiting for attacks...\n')

    for message in consumer:
        log = message.value
        result = analyze_attack(log)
        print_threat_report(result)


if __name__ == '__main__':
    start_consumer()