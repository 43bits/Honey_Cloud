# ml_models/risk_scorer.py

HIGH_RISK_ATTACKS = [
    'Database Attack',
    'SSH Brute Force',
    'Telnet Attack',
    'SMB Attack',
]

MEDIUM_RISK_ATTACKS = [
    'Web Exploit',
    'FTP Attack',
    'Email Attack',
    'DNS Attack',
]

CRITICAL_PORTS = [
    3306, 5432, 1433, 27017, 6379,
    22, 3389, 445, 139, 135, 9200,
]

HIGH_RISK_PORTS = [23, 21, 8080, 8443, 25, 587]


# def calculate_risk_score(attack_type, confidence, is_anomaly,
#                          anomaly_score, dst_port, campaign):
#     """
#     Returns a risk level and numeric score (0-100).
#     """
#     score = 0

#     # Base score from attack type
#     if attack_type in HIGH_RISK_ATTACKS:
#         score += 40
#     elif attack_type in MEDIUM_RISK_ATTACKS:
#         score += 25
#     else:
#         score += 10

#     # Boost for high confidence
#     score += int(confidence * 0.3)   # max +30

#     # Boost for anomaly
#     if is_anomaly:
#         score += 20

#     # Boost for critical ports
#     if dst_port in CRITICAL_PORTS:
#         score += 15
#     elif dst_port in HIGH_RISK_PORTS:
#         score += 8

#     # Cap at 100
#     score = min(score, 100)

#     # Risk level label
#     if score >= 75:
#         level = 'CRITICAL'
#         emoji = '🔴'
#     elif score >= 50:
#         level = 'HIGH'
#         emoji = '🟠'
#     elif score >= 25:
#         level = 'MEDIUM'
#         emoji = '🟡'
#     else:
#         level = 'LOW'
#         emoji = '🟢'

#     return score, level, emoji

# ml_models/risk_scorer.py — update calculate_risk_score




 
def calculate_risk_score(attack_type, confidence, is_anomaly,
                         anomaly_score, dst_port, campaign,
                         login_attempts=1, connection_rate=1.0):
    """
    Score 0-100. Uses login_attempts and connection_rate
    so background noise stays LOW even if classifier is confident.
    """
    score = 0

    # ── Intensity check FIRST ──────────────────────
    # Single-hit low-rate traffic → cap score early
    login_attempts  = int(login_attempts  or 1)
    connection_rate = float(connection_rate or 1.0)

    is_background = (
        login_attempts  <= 2   and
        connection_rate <= 3.0
    )

    if is_background:
        # Background noise — never goes above MEDIUM
        # even if classifier says Web Exploit at 100%
        if attack_type in HIGH_RISK_ATTACKS and dst_port in CRITICAL_PORTS:
            return 24, 'LOW', '🟢'   # still LOW — single hit on critical port
        else:
            return 10, 'LOW', '🟢'

    # ── Normal scoring for real attacks ───────────
    # Base score from attack type
    if attack_type in HIGH_RISK_ATTACKS:
        score += 40
    elif attack_type in MEDIUM_RISK_ATTACKS:
        score += 20
    else:
        score += 5

    # Confidence boost — only meaningful above 60%
    if confidence >= 60:
        score += int(confidence * 0.15)   # max +15

    # Anomaly boost
    if is_anomaly:
        score += 20

    # Port boost — only if real attack volume
    if login_attempts >= 10:
        if dst_port in CRITICAL_PORTS and attack_type in HIGH_RISK_ATTACKS:
            score += 15
        elif dst_port in HIGH_RISK_PORTS:
            score += 5

    # Volume boost — high rate = more dangerous
    if connection_rate > 20:
        score += 10
    elif connection_rate > 10:
        score += 5

    score = min(score, 100)

    if score >= 75:   return score, 'CRITICAL', '🔴'
    elif score >= 50: return score, 'HIGH',     '🟠'
    elif score >= 25: return score, 'MEDIUM',   '🟡'
    else:             return score, 'LOW',       '🟢'
    
    


