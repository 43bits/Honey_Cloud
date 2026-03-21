# ai_agents/threat_intel_engine.py — COMPLETE REWRITE
"""
Professional Threat Intelligence Enrichment Engine
Cross-correlates AbuseIPDB + VirusTotal + ML models
into a calibrated Threat Intel Score (0-100).
"""

import os
import time
import json
import urllib.request
import urllib.error
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ABUSEIPDB_KEY  = os.getenv('ABUSEIPDB_API_KEY',  '').strip()
VIRUSTOTAL_KEY = os.getenv('VIRUSTOTAL_API_KEY',  '').strip()

# ── Thread-safe cache ──────────────────────────────
_cache      : dict  = {}
_cache_lock         = threading.Lock()
CACHE_TTL           = 3600  # 1 hour


def _cache_get(ip: str) -> dict | None:
    with _cache_lock:
        entry = _cache.get(ip)
        if not entry:
            return None
        if time.time() - entry['ts'] > CACHE_TTL:
            del _cache[ip]
            return None
        return entry['data']


def _cache_set(ip: str, data: dict):
    with _cache_lock:
        _cache[ip] = {'data': data, 'ts': time.time()}


# ── IP validation ──────────────────────────────────
PRIVATE_RANGES = (
    '10.', '172.16.', '172.17.', '172.18.', '172.19.',
    '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
    '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
    '172.30.', '172.31.', '192.168.', '127.', '0.',
    'localhost', '::1',
)

def is_private_ip(ip: str) -> bool:
    return any(ip.startswith(r) for r in PRIVATE_RANGES)


# ── HTTP helper ────────────────────────────────────
def _http_get(url: str, headers: dict,
              timeout: int = 6) -> dict | None:
    """
    Simple HTTP GET — returns parsed JSON or None on error.
    Never raises — always returns safely.
    """
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        print(f"[TI] HTTP {e.code} from {url.split('/')[2]}: {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"[TI] Network error: {e.reason}")
        return None
    except json.JSONDecodeError:
        print(f"[TI] JSON decode error from {url.split('/')[2]}")
        return None
    except Exception as e:
        print(f"[TI] Unexpected error: {e}")
        return None


# ── AbuseIPDB ──────────────────────────────────────
EMPTY_ABUSE = {
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
    'error':              None,
}


def query_abuseipdb(ip: str) -> dict:
    if not ABUSEIPDB_KEY:
        return {**EMPTY_ABUSE, 'error': 'API key not configured'}

    url = (
        f'https://api.abuseipdb.com/api/v2/check'
        f'?ipAddress={ip}&maxAgeInDays=90&verbose'
    )
    raw = _http_get(url, {
        'Key':    ABUSEIPDB_KEY,
        'Accept': 'application/json',
    })

    if raw is None:
        return {**EMPTY_ABUSE, 'error': 'API request failed'}

    if 'errors' in raw:
        err = raw['errors'][0].get('detail', 'Unknown error')
        print(f"[TI] AbuseIPDB error: {err}")
        return {**EMPTY_ABUSE, 'error': err}

    data = raw.get('data', {})
    if not data:
        return {**EMPTY_ABUSE, 'error': 'Empty response'}

    return {
        'available':          True,
        'abuse_confidence':   int(data.get('abuseConfidenceScore', 0)),
        'total_reports':      int(data.get('totalReports', 0)),
        'distinct_reporters': int(data.get('numDistinctUsers', 0)),
        'last_reported':      data.get('lastReportedAt'),
        'country_code':       data.get('countryCode'),
        'isp':                data.get('isp', ''),
        'domain':             data.get('domain', ''),
        'is_whitelisted':     bool(data.get('isWhitelisted', False)),
        'usage_type':         data.get('usageType', ''),
        'error':              None,
    }


# ── VirusTotal ─────────────────────────────────────
EMPTY_VT = {
    'available':        False,
    'malicious_votes':  0,
    'suspicious_votes': 0,
    'harmless_votes':   0,
    'undetected_votes': 0,
    'total_engines':    0,
    'malicious_ratio':  0.0,
    'reputation':       0,
    'categories':       [],
    'last_analysis':    None,
    'error':            None,
}


def query_virustotal(ip: str) -> dict:
    if not VIRUSTOTAL_KEY:
        return {**EMPTY_VT, 'error': 'API key not configured'}

    url = f'https://www.virustotal.com/api/v3/ip_addresses/{ip}'
    raw = _http_get(url, {'x-apikey': VIRUSTOTAL_KEY})

    if raw is None:
        return {**EMPTY_VT, 'error': 'API request failed'}

    if 'error' in raw:
        err = raw['error'].get('message', 'Unknown error')
        print(f"[TI] VirusTotal error: {err}")
        return {**EMPTY_VT, 'error': err}

    attrs = raw.get('data', {}).get('attributes', {})
    if not attrs:
        return {**EMPTY_VT, 'error': 'No attributes in response'}

    stats      = attrs.get('last_analysis_stats', {})
    malicious  = int(stats.get('malicious',  0))
    suspicious = int(stats.get('suspicious', 0))
    harmless   = int(stats.get('harmless',   0))
    undetected = int(stats.get('undetected', 0))
    total      = malicious + suspicious + harmless + undetected
    ratio      = round(malicious / max(total, 1) * 100, 1)

    # Categories: dict of {engine: category} — deduplicate values
    cat_dict   = attrs.get('categories', {})
    categories = list(set(cat_dict.values()))[:5]

    return {
        'available':        True,
        'malicious_votes':  malicious,
        'suspicious_votes': suspicious,
        'harmless_votes':   harmless,
        'undetected_votes': undetected,
        'total_engines':    total,
        'malicious_ratio':  ratio,
        'reputation':       int(attrs.get('reputation', 0)),
        'categories':       categories,
        'last_analysis':    attrs.get('last_analysis_date'),
        'error':            None,
    }


# ── Professional cross-correlation ────────────────
#
# Scoring philosophy:
#   Each source contributes a weighted sub-score.
#   Sources are independent — a zero from one source
#   does not cancel a high score from another.
#   Final score uses the MAXIMUM of individual source
#   scores as a floor — a confirmed malicious IP from
#   AbuseIPDB is CONFIRMED regardless of VT being 0.
#
#   Weight allocation:
#     AbuseIPDB  → up to 45 pts (community intelligence)
#     VirusTotal → up to 40 pts (vendor intelligence)
#     ML model   → up to 15 pts (behavioral intelligence)
#     Modifiers  → ±10 pts    (context adjustments)

def _score_abuseipdb(abuse: dict) -> tuple[int, list, list]:
    """Returns (score, evidence_lines, threat_tags)."""
    if not abuse.get('available'):
        return 0, [], []

    score    = 0
    evidence = []
    tags     = []
    ac       = abuse['abuse_confidence']
    reports  = abuse['total_reports']
    distinct = abuse['distinct_reporters']

    # Primary confidence score (0-45)
    if ac >= 90:
        score += 45
        evidence.append(
            f'AbuseIPDB: {ac}% confidence — confirmed malicious IP'
        )
        tags.append('CONFIRMED_MALICIOUS')
    elif ac >= 75:
        score += 35
        evidence.append(
            f'AbuseIPDB: {ac}% confidence — highly suspicious'
        )
        tags.append('HIGHLY_SUSPICIOUS')
    elif ac >= 50:
        score += 24
        evidence.append(
            f'AbuseIPDB: {ac}% confidence — suspicious activity'
        )
    elif ac >= 25:
        score += 14
        evidence.append(
            f'AbuseIPDB: {ac}% confidence — minor reports'
        )
    elif ac >= 5:
        score += 6
        evidence.append(
            f'AbuseIPDB: {ac}% confidence — low suspicion'
        )

    # Report volume boost (0-8)
    if reports >= 500:
        score += 8
        evidence.append(
            f'{reports:,} abuse reports from '
            f'{distinct} distinct reporters'
        )
        tags.append('REPEAT_OFFENDER')
    elif reports >= 100:
        score += 5
        evidence.append(f'{reports} abuse reports')
    elif reports >= 10:
        score += 2
        evidence.append(f'{reports} abuse reports')

    # Whitelist reduction
    if abuse.get('is_whitelisted'):
        score = max(0, score - 25)
        evidence.append('IP is AbuseIPDB-whitelisted — score reduced')

    # Usage type context
    usage = (abuse.get('usage_type') or '').lower()
    if any(t in usage for t in ['tor', 'vpn', 'proxy']):
        score += 6
        evidence.append(f'Usage type: {usage} — anonymization detected')
        tags.append('ANONYMIZED')
    elif 'hosting' in usage or 'datacenter' in usage:
        score += 3
        evidence.append(f'Usage type: {usage}')

    return min(score, 45), evidence, tags


def _score_virustotal(vt: dict) -> tuple[int, list, list]:
    """Returns (score, evidence_lines, threat_tags)."""
    if not vt.get('available'):
        return 0, [], []

    score    = 0
    evidence = []
    tags     = []
    mv       = vt['malicious_votes']
    sv       = vt['suspicious_votes']
    ratio    = vt['malicious_ratio']
    rep      = vt['reputation']
    total    = vt['total_engines']

    # Primary malicious vote score (0-40)
    if mv >= 20 or ratio >= 30:
        score += 40
        evidence.append(
            f'VirusTotal: {mv}/{total} engines flagged malicious '
            f'({ratio}%)'
        )
        tags.append('VT_MALICIOUS')
    elif mv >= 10 or ratio >= 15:
        score += 30
        evidence.append(
            f'VirusTotal: {mv}/{total} engines flagged ({ratio}%)'
        )
        tags.append('VT_SUSPICIOUS')
    elif mv >= 5 or ratio >= 7:
        score += 20
        evidence.append(
            f'VirusTotal: {mv} engine detections ({ratio}%)'
        )
    elif mv >= 2 or ratio >= 3:
        score += 10
        evidence.append(
            f'VirusTotal: {mv} engine detections'
        )
    elif mv >= 1:
        score += 5
        evidence.append('VirusTotal: 1 engine detection')

    # Suspicious votes (secondary signal)
    if sv >= 10:
        score += 6
        evidence.append(f'{sv} additional suspicious votes')
    elif sv >= 5:
        score += 3

    # Community reputation
    if rep <= -100:
        score += 8
        evidence.append(
            f'VirusTotal reputation: {rep} (severely negative)'
        )
        tags.append('BAD_REPUTATION')
    elif rep <= -50:
        score += 5
        evidence.append(f'VirusTotal reputation: {rep} (negative)')
    elif rep <= -10:
        score += 2

    # Category tags
    cats = [c.lower() for c in vt.get('categories', [])]
    if any('malware' in c for c in cats):
        score += 5
        tags.append('MALWARE_DISTRIBUTION')
        evidence.append('Categorized as malware distribution')
    if any('phishing' in c for c in cats):
        score += 4
        tags.append('PHISHING')
        evidence.append('Categorized as phishing')
    if any('spam' in c for c in cats):
        score += 2
        tags.append('SPAM')

    return min(score, 40), evidence, tags


def _score_ml(ml_risk_score: int,
              attack_type: str,
              is_anomaly: bool) -> tuple[int, list]:
    """Returns (score, evidence_lines)."""
    score    = 0
    evidence = []

    # ML risk score contribution (0-10)
    if ml_risk_score >= 85:
        score += 10
        evidence.append(
            f'ML model: risk score {ml_risk_score}/100 '
            f'(trained on 14.2M attacks)'
        )
    elif ml_risk_score >= 65:
        score += 7
        evidence.append(f'ML model: risk score {ml_risk_score}/100')
    elif ml_risk_score >= 40:
        score += 4
        evidence.append(f'ML model: risk score {ml_risk_score}/100')

    # Anomaly flag (0-3)
    if is_anomaly:
        score += 3
        evidence.append('ML anomaly detector: deviation from baseline')

    # Attack type criticality (0-2)
    CRITICAL_ATTACKS = {
        'Database Attack', 'SMB Attack',
        'Telnet Attack', 'SSH Brute Force',
    }
    if attack_type in CRITICAL_ATTACKS:
        score += 2

    return min(score, 15), evidence


def calculate_threat_intel_score(
    abuse:         dict,
    virustotal:    dict,
    ml_risk_score: int  = 0,
    attack_type:   str  = '',
    is_anomaly:    bool = False,
) -> dict:
    """
    Professional cross-correlation of all intel sources.
    Each source scored independently then combined.
    """
    abuse_score, abuse_ev, abuse_tags = _score_abuseipdb(abuse)
    vt_score,    vt_ev,    vt_tags    = _score_virustotal(virustotal)
    ml_score,    ml_ev                = _score_ml(
        ml_risk_score, attack_type, is_anomaly
    )

    # Combination strategy:
    # Take the higher of (abuse, vt) as primary signal
    # Add ML as secondary signal
    # Apply small bonus when multiple sources agree
    primary   = max(abuse_score, vt_score)
    secondary = min(abuse_score, vt_score)

    # Corroboration bonus: both sources independently flagging
    # the same IP increases confidence
    corroboration = 0
    if abuse_score >= 20 and vt_score >= 15:
        corroboration = 8
    elif abuse_score >= 10 and vt_score >= 10:
        corroboration = 4

    final_score = min(
        primary + (secondary // 3) + ml_score + corroboration,
        100
    )

    # Combine all evidence and tags
    all_evidence = abuse_ev + vt_ev + ml_ev
    all_tags     = list(set(abuse_tags + vt_tags))

    # Determine active sources
    sources = []
    if abuse.get('available'):
        sources.append('AbuseIPDB')
    if virustotal.get('available'):
        sources.append('VirusTotal')
    sources.append(f'HoneyCloud ML ({ml_risk_score}/100)')

    # Classification and recommendation
    if final_score >= 75:
        level  = 'CONFIRMED_THREAT'
        color  = '#ff2d2d'
        rec    = (
            'Block this IP at perimeter firewall immediately. '
            'Add to blocklist. Correlate with other logs for '
            'potential breach indicators. Notify SOC team.'
        )
    elif final_score >= 55:
        level  = 'HIGH_CONFIDENCE'
        color  = '#ff6b00'
        rec    = (
            'Add to watchlist with elevated monitoring. '
            'Consider rate-limiting or temporary block. '
            'Review all recent connections from this IP.'
        )
    elif final_score >= 30:
        level  = 'SUSPICIOUS'
        color  = '#ffe600'
        rec    = (
            'Monitor this IP with increased logging. '
            'No immediate block required. '
            'Re-evaluate if activity continues.'
        )
    elif final_score >= 10:
        level  = 'LOW_RISK'
        color  = '#00ffe7'
        rec    = (
            'Low risk. Continue standard monitoring. '
            'No action required at this time.'
        )
    else:
        level  = 'CLEAN'
        color  = '#00ff88'
        rec    = (
            'No threat indicators found across all sources. '
            'IP appears clean.'
        )

    return {
        'threat_intel_score':  final_score,
        'intel_level':         level,
        'intel_color':         color,
        'evidence':            all_evidence,
        'threat_tags':         all_tags,
        'recommendation':      rec,
        'data_sources':        sources,
        'score_breakdown': {
            'abuseipdb':      abuse_score,
            'virustotal':     vt_score,
            'ml_model':       ml_score,
            'corroboration':  corroboration,
        },
        'abuseipdb':           abuse,
        'virustotal':          virustotal,
        'enriched_at':         datetime.now().isoformat(),
    }


# ── Main enrichment function ───────────────────────

def enrich_attack(attack: dict) -> dict:
    """
    Full enrichment pipeline for a single attack.
    Cached per IP for 1 hour.
    """
    ip = str(attack.get('source_ip', '')).strip()

    if not ip or is_private_ip(ip):
        return {
            **attack,
            'threat_intel_score': 0,
            'intel_level':        'LOCAL',
            'intel_color':        '#00ffe7',
            'evidence':           ['Private or local IP — skipped'],
            'threat_tags':        [],
            'recommendation':     'Local traffic — no action needed.',
            'data_sources':       ['HoneyCloud ML'],
            'score_breakdown':    {},
            'enriched_at':        datetime.now().isoformat(),
        }

    cached = _cache_get(ip)
    if cached:
        print(f"[TI] Cache hit: {ip}")
        return {**attack, **cached}

    print(f"[TI] Querying intel for {ip}...")
    t_start = time.time()

    abuse      = query_abuseipdb(ip)
    virustotal = query_virustotal(ip)

    intel = calculate_threat_intel_score(
        abuse         = abuse,
        virustotal    = virustotal,
        ml_risk_score = int(attack.get('risk_score', 0)),
        attack_type   = str(attack.get('attack_type', '')),
        is_anomaly    = bool(attack.get('is_anomaly', False)),
    )

    _cache_set(ip, intel)

    elapsed = round(time.time() - t_start, 2)
    print(
        f"[TI] {ip} → {intel['intel_level']} "
        f"score={intel['threat_intel_score']} "
        f"(abuse={intel['score_breakdown'].get('abuseipdb',0)} "
        f"vt={intel['score_breakdown'].get('virustotal',0)} "
        f"ml={intel['score_breakdown'].get('ml_model',0)}) "
        f"in {elapsed}s"
    )

    return {**attack, **intel}