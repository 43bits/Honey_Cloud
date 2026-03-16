# scripts/test_scorer.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_models.feature_engineering import engineer_features_from_live_log
from ml_models.anomaly_detection import predict_anomaly
from ml_models.attack_classifier import predict_attack_type
from ml_models.clustering import predict_cluster
from ml_models.risk_scorer import calculate_risk_score

# These should be LOW
# scripts/test_scorer.py — update test cases to include login_attempts

test_cases = [
    # These should be LOW — single hit, low rate
    {'source_ip': '1.2.3.4', 'source_port': 54321,
     'port_targeted': 80,  'protocol': 'tcp', 'country': 'USA',
     'login_attempts': 1,  'connection_rate': 0.5,
     'description': 'Port 80 single hit — background'},

    {'source_ip': '1.2.3.5', 'source_port': 54322,
     'port_targeted': 443, 'protocol': 'tcp', 'country': 'Germany',
     'login_attempts': 1,  'connection_rate': 0.3,
     'description': 'Port 443 single hit — background'},

    {'source_ip': '1.2.3.6', 'source_port': 54323,
     'port_targeted': 53,  'protocol': 'udp', 'country': 'France',
     'login_attempts': 1,  'connection_rate': 0.2,
     'description': 'DNS single query — background'},

    # These should be MEDIUM/HIGH — real attack volume
    {'source_ip': '91.240.118.5', 'source_port': 54324,
     'port_targeted': 22,  'protocol': 'tcp', 'country': 'Russia',
     'login_attempts': 250, 'connection_rate': 35.0,
     'description': 'SSH brute force — real attack'},

    {'source_ip': '185.234.219.4', 'source_port': 54325,
     'port_targeted': 3306, 'protocol': 'tcp', 'country': 'China',
     'login_attempts': 80,  'connection_rate': 15.0,
     'description': 'DB attack — real attack'},

    {'source_ip': '103.27.186.5', 'source_port': 54326,
     'port_targeted': 80,  'protocol': 'tcp', 'country': 'China',
     'login_attempts': 45,  'connection_rate': 12.0,
     'description': 'Web exploit — real attack'},
]
print("=" * 60)
print("  Risk Scorer Test — should all be LOW")
print("=" * 60)

for test in test_cases:
    desc = test.pop('description')
    features = engineer_features_from_live_log(test)

    is_anomaly, anomaly_score = predict_anomaly(features)
    attack_type, confidence   = predict_attack_type(features)
    campaign                  = predict_cluster(features)
    risk_score, risk_level, emoji = calculate_risk_score(
        attack_type, confidence, is_anomaly,
        anomaly_score, test['port_targeted'], campaign
    )

    print(f"\n  {desc}")
    print(f"  attack_type : {attack_type}")
    print(f"  confidence  : {confidence}%")
    print(f"  is_anomaly  : {is_anomaly}")
    print(f"  risk_score  : {risk_score}")
    print(f"  risk_level  : {emoji} {risk_level}")