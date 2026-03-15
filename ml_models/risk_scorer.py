# ml_models/risk_scorer.py

# High-risk attack types
HIGH_RISK_ATTACKS = ['Database Attack', 'SSH Brute Force', 'Telnet Attack']
MEDIUM_RISK_ATTACKS = ['Web Exploit', 'FTP Attack']

# Ports that are critical if attacked
CRITICAL_PORTS = [3306, 5432, 1433, 27017, 6379, 22, 3389, 445]
HIGH_RISK_PORTS = [23, 21, 8080, 8443]


def calculate_risk_score(attack_type, confidence, is_anomaly,
                         anomaly_score, dst_port, campaign):
    """
    Returns a risk level and numeric score (0-100).
    """
    score = 0

    # Base score from attack type
    if attack_type in HIGH_RISK_ATTACKS:
        score += 40
    elif attack_type in MEDIUM_RISK_ATTACKS:
        score += 25
    else:
        score += 10

    # Boost for high confidence
    score += int(confidence * 0.3)   # max +30

    # Boost for anomaly
    if is_anomaly:
        score += 20

    # Boost for critical ports
    if dst_port in CRITICAL_PORTS:
        score += 15
    elif dst_port in HIGH_RISK_PORTS:
        score += 8

    # Cap at 100
    score = min(score, 100)

    # Risk level label
    if score >= 75:
        level = 'CRITICAL'
        emoji = '🔴'
    elif score >= 50:
        level = 'HIGH'
        emoji = '🟠'
    elif score >= 25:
        level = 'MEDIUM'
        emoji = '🟡'
    else:
        level = 'LOW'
        emoji = '🟢'

    return score, level, emoji