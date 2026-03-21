# ai_agents/threat_intel_engine.py
"""
Phase A — Threat Intelligence Enrichment Engine

Queries AbuseIPDB + VirusTotal for every attacker IP.
Cross-correlates results into a single Threat Intel Score (0-100).
No LLM required — intelligence comes from real threat databases.
"""

import os
import time
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ABUSEIPDB_KEY  = os.getenv('ABUSEIPDB_API_KEY', '')
VIRUSTOTAL_KEY = os.getenv('VIRUSTOTAL_API_KEY', '')

# ── Simple in-memory cache ─────────────────────────
# Avoids re-querying the same IP within 1 hour
# In production this would be Redis
_cache: dict = {}
CACHE_TTL = 3600  # 1 hour in seconds


def _cache_get(ip: str) -> dict | None:
    entry = _cache.get(ip)
    if not entry:
        return None
    if time.time() - entry['cached_at'] > CACHE_TTL:
        del _cache[ip]
        return None
    return entry['data']


def _cache_set(ip: str, data: dict):
    _cache[ip] = {
        'data':      data,
        'cached_at': time.time(),
    }


# ── AbuseIPDB lookup ───────────────────────────────

def query_abuseipdb(ip: str) -> dict:
    """
    Query AbuseIPDB for community abuse reports.
    Returns structured result regardless of API availability.
    """
    if not ABUSEIPDB_KEY:
        return {
            'available':          False,
            'abuse_confidence':   0,
            'total_reports':      0,
            'distinct_reporters': 0,
            'last_reported':      None,
            'country_code':       None,
            'isp':                None,
            'domain':             None,
            'is_whitelisted':     False,
            'usage_type':         None,
        }

    try:
        url    = f'https://api.abuseipdb.com/api/v2/check'
        params = f'?ipAddress={ip}&maxAgeInDays=90&verbose'
        req    = urllib.request.Request(
            url + params,
            headers={
                'Key':    ABUSEIPDB_KEY,
                'Accept': 'application/json',
            }
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            raw  = json.loads(r.read())
            data = raw.get('data', {})
            return {
                'available':          True,
                'abuse_confidence':   int(data.get('abuseConfidenceScore', 0)),
                'total_reports':      int(data.get('totalReports', 0)),
                'distinct_reporters': int(data.get('numDistinctUsers', 0)),
                'last_reported':      data.get('lastReportedAt'),
                'country_code':       data.get('countryCode'),
                'isp':                data.get('isp'),
                'domain':             data.get('domain'),
                'is_whitelisted':     bool(data.get('isWhitelisted', False)),
                'usage_type':         data.get('usageType'),
            }
    except Exception as e:
        print(f"[TI] AbuseIPDB error for {ip}: {e}")
        return {
            'available':          False,
            'abuse_confidence':   0,
            'total_reports':      0,
            'distinct_reporters': 0,
            'last_reported':      None,
            'country_code':       None,
            'isp':                None,
            'domain':             None,
            'is_whitelisted':     False,
            'usage_type':         None,
        }


# ── VirusTotal lookup ──────────────────────────────

def query_virustotal(ip: str) -> dict:
    """
    Query VirusTotal for malware/phishing associations.
    Returns structured result regardless of API availability.
    """
    if not VIRUSTOTAL_KEY:
        return {
            'available':         False,
            'malicious_votes':   0,
            'suspicious_votes':  0,
            'harmless_votes':    0,
            'total_engines':     0,
            'malicious_ratio':   0.0,
            'reputation':        0,
            'categories':        [],
            'last_analysis':     None,
        }

    try:
        url = f'https://www.virustotal.com/api/v3/ip_addresses/{ip}'
        req = urllib.request.Request(
            url,
            headers={ 'x-apikey': VIRUSTOTAL_KEY }
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            raw        = json.loads(r.read())
            attrs      = raw.get('data', {}).get('attributes', {})
            stats      = attrs.get('last_analysis_stats', {})
            malicious  = int(stats.get('malicious',  0))
            suspicious = int(stats.get('suspicious', 0))
            harmless   = int(stats.get('harmless',   0))
            total      = malicious + suspicious + harmless + \
                         int(stats.get('undetected', 0))
            ratio      = round(malicious / max(total, 1) * 100, 1)
            categories = list(attrs.get('categories', {}).values())

            return {
                'available':        True,
                'malicious_votes':  malicious,
                'suspicious_votes': suspicious,
                'harmless_votes':   harmless,
                'total_engines':    total,
                'malicious_ratio':  ratio,
                'reputation':       int(attrs.get('reputation', 0)),
                'categories':       categories[:5],
                'last_analysis':    attrs.get('last_analysis_date'),
            }
    except Exception as e:
        print(f"[TI] VirusTotal error for {ip}: {e}")
        return {
            'available':        False,
            'malicious_votes':  0,
            'suspicious_votes': 0,
            'harmless_votes':   0,
            'total_engines':    0,
            'malicious_ratio':  0.0,
            'reputation':       0,
            'categories':       [],
            'last_analysis':    None,
        }


# ── Cross-correlation engine ───────────────────────

def calculate_threat_intel_score(
    abuse: dict,
    virustotal: dict,
    ml_risk_score: int,
    attack_type: str,
) -> dict:
    """
    Cross-correlates AbuseIPDB + VirusTotal + our ML models
    into a single Threat Intel Score (0-100).

    This replaces any LLM — the intelligence is real data.
    """
    score       = 0
    evidence    = []
    threat_tags = []

    # ── AbuseIPDB contribution (max 40 points) ─────
    if abuse.get('available'):
        ac = abuse['abuse_confidence']

        if ac >= 90:
            score += 40
            evidence.append(f"AbuseIPDB: {ac}% confidence — known malicious")
            threat_tags.append('KNOWN_MALICIOUS')
        elif ac >= 70:
            score += 30
            evidence.append(f"AbuseIPDB: {ac}% confidence — highly suspicious")
            threat_tags.append('HIGHLY_SUSPICIOUS')
        elif ac >= 40:
            score += 20
            evidence.append(f"AbuseIPDB: {ac}% confidence — suspicious activity")
        elif ac >= 10:
            score += 10
            evidence.append(f"AbuseIPDB: {ac}% confidence — minor reports")

        if abuse['total_reports'] > 100:
            score += 5
            evidence.append(f"{abuse['total_reports']} community abuse reports")
            threat_tags.append('REPEAT_OFFENDER')

        if abuse['is_whitelisted']:
            score = max(0, score - 20)
            evidence.append("IP is whitelisted — score reduced")

        usage = abuse.get('usage_type', '')
        if usage and any(t in usage.lower()
                         for t in ['vpn', 'tor', 'proxy', 'hosting']):
            score += 8
            evidence.append(f"Usage type: {usage} — anonymization likely")
            threat_tags.append('ANONYMIZED')

    # ── VirusTotal contribution (max 35 points) ────
    if virustotal.get('available'):
        ratio = virustotal['malicious_ratio']
        mv    = virustotal['malicious_votes']

        if ratio >= 20:
            score += 35
            evidence.append(
                f"VirusTotal: {mv} engines flagged as malicious ({ratio}%)"
            )
            threat_tags.append('VIRUSTOTAL_MALICIOUS')
        elif ratio >= 10:
            score += 22
            evidence.append(
                f"VirusTotal: {mv} engines flagged ({ratio}%)"
            )
        elif ratio >= 3:
            score += 12
            evidence.append(
                f"VirusTotal: {mv} suspicious detections"
            )

        if virustotal['suspicious_votes'] > 5:
            score += 5
            evidence.append(
                f"{virustotal['suspicious_votes']} additional suspicious votes"
            )

        rep = virustotal['reputation']
        if rep < -50:
            score += 10
            evidence.append(f"VirusTotal reputation: {rep} (very negative)")
            threat_tags.append('BAD_REPUTATION')
        elif rep < -10:
            score += 5
            evidence.append(f"VirusTotal reputation: {rep} (negative)")

        cats = virustotal.get('categories', [])
        if any('malware' in c.lower() for c in cats):
            score += 8
            threat_tags.append('MALWARE_DISTRIBUTION')
        if any('phishing' in c.lower() for c in cats):
            score += 6
            threat_tags.append('PHISHING')

    # ── ML model contribution (max 25 points) ──────
    # Uses our trained Random Forest risk score
    # This is where our 14.2M dataset training pays off
    if ml_risk_score >= 85:
        score += 25
        evidence.append(f"ML risk score: {ml_risk_score}/100 (CRITICAL)")
    elif ml_risk_score >= 65:
        score += 18
        evidence.append(f"ML risk score: {ml_risk_score}/100 (HIGH)")
    elif ml_risk_score >= 40:
        score += 10
        evidence.append(f"ML risk score: {ml_risk_score}/100 (MEDIUM)")

    # Attack type modifier
    HIGH_VALUE_ATTACKS = ['Database Attack', 'SMB Attack', 'Telnet Attack']
    if attack_type in HIGH_VALUE_ATTACKS:
        score += 5
        evidence.append(f"High-value target attack: {attack_type}")

    # ── Final score and classification ────────────
    score = min(score, 100)

    if score >= 80:
        intel_level = 'CONFIRMED_THREAT'
        intel_color = '#ff2d2d'
        recommendation = (
            'Block this IP at perimeter firewall immediately. '
            'Correlate with other logs for potential breach indicators.'
        )
    elif score >= 60:
        intel_level = 'HIGH_CONFIDENCE'
        intel_color = '#ff6b00'
        recommendation = (
            'Add to watchlist. Monitor for repeated attempts. '
            'Consider temporary rate limiting.'
        )
    elif score >= 35:
        intel_level = 'SUSPICIOUS'
        intel_color = '#ffe600'
        recommendation = (
            'Monitor this IP. Increase logging verbosity. '
            'No immediate action required.'
        )
    else:
        intel_level = 'LOW_RISK'
        intel_color = '#00ffe7'
        recommendation = 'No action required. Logging only.'

    return {
        'threat_intel_score':  score,
        'intel_level':         intel_level,
        'intel_color':         intel_color,
        'evidence':            evidence,
        'threat_tags':         threat_tags,
        'recommendation':      recommendation,
        'abuseipdb':           abuse,
        'virustotal':          virustotal,
        'enriched_at':         datetime.now().isoformat(),
        'data_sources':        [
            s for s, d in [
                ('AbuseIPDB',  abuse),
                ('VirusTotal', virustotal),
            ] if d.get('available')
        ] + ['HoneyCloud ML (14.2M trained)'],
    }


# ── Main enrichment function ───────────────────────

def enrich_attack(attack: dict) -> dict:
    """
    Full enrichment pipeline for a single attack.
    Returns enriched attack dict with threat intel fields added.
    Cached per IP to avoid duplicate API calls.
    """
    ip = attack.get('source_ip', '')

    # Skip private/local IPs
    if ip.startswith(('192.168.', '10.', '172.16.',
                      '127.', 'localhost', '0.')):
        return {
            **attack,
            'threat_intel_score': 0,
            'intel_level':        'LOCAL',
            'intel_color':        '#00ffe7',
            'evidence':           ['Private/local IP — no enrichment'],
            'threat_tags':        [],
            'recommendation':     'Local traffic — no action needed.',
            'data_sources':       [],
            'enriched_at':        datetime.now().isoformat(),
        }

    # Check cache first
    cached = _cache_get(ip)
    if cached:
        print(f"[TI] Cache hit for {ip}")
        return {**attack, **cached}

    print(f"[TI] Enriching {ip}...")

    # Query both sources
    abuse      = query_abuseipdb(ip)
    virustotal = query_virustotal(ip)

    # Cross-correlate with our ML score
    intel = calculate_threat_intel_score(
        abuse         = abuse,
        virustotal    = virustotal,
        ml_risk_score = int(attack.get('risk_score', 0)),
        attack_type   = str(attack.get('attack_type', '')),
    )

    # Cache the result
    _cache_set(ip, intel)

    enriched = {**attack, **intel}

    print(
        f"[TI] {ip} → {intel['intel_level']} "
        f"(score: {intel['threat_intel_score']}) "
        f"sources: {intel['data_sources']}"
    )

    return enriched


# ── Batch enrichment ───────────────────────────────

def enrich_batch(attacks: list, limit: int = 20) -> list:
    """
    Enrich a list of attacks.
    limit: max attacks to enrich per call (API rate limit protection)
    """
    enriched = []
    count    = 0

    for attack in attacks:
        ip = attack.get('source_ip', '')
        # Only enrich if not already enriched and not cached
        if attack.get('threat_intel_score') is not None:
            enriched.append(attack)
            continue

        if count >= limit:
            enriched.append(attack)
            continue

        enriched.append(enrich_attack(attack))
        count += 1

        # Respect VirusTotal rate limit (4/min)
        if count % 4 == 0:
            time.sleep(15)

    return enriched