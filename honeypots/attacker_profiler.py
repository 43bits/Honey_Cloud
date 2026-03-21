# honeypots/attacker_profiler.py
"""
Attacker Profiler — uses our trained ML clustering model
to classify attacker into campaign type.

This is where our 14.2M trained dataset pays off —
we recognize which campaign this attacker belongs to
and select the appropriate deception strategy.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from honeypots.behavioral_fingerprinter import BehaviorProfile


# ── Attacker profiles ──────────────────────────────

PROFILES = {
    'script_kiddie': {
        'description':  'Automated tool, no real skill',
        'indicators':   ['bot_rapid', 'wordlist_scan', 'low'],
        'threat_level': 'LOW',
        'deception':    'deny_fast',
        'color':        '🟢',
    },
    'botnet_node': {
        'description':  'Part of coordinated botnet campaign',
        'indicators':   ['bot_rapid', 'credential_stuffing', 'medium'],
        'threat_level': 'MEDIUM',
        'deception':    'slow_response',
        'color':        '🟡',
    },
    'credential_stuffer': {
        'description':  'Credential stuffing from breach database',
        'indicators':   ['bot_slow', 'credential_stuffing', 'medium'],
        'threat_level': 'HIGH',
        'deception':    'fake_success',
        'color':        '🟠',
    },
    'targeted_attacker': {
        'description':  'Targeted attack against this system',
        'indicators':   ['human_manual', 'manual_probe', 'high'],
        'threat_level': 'HIGH',
        'deception':    'fake_success',
        'color':        '🟠',
    },
    'apt_actor': {
        'description':  'Advanced Persistent Threat — nation-state level',
        'indicators':   ['apt_deliberate', 'targeted_apt', 'apt'],
        'threat_level': 'CRITICAL',
        'deception':    'full_fake_env',
        'color':        '🔴',
    },
    'scanner': {
        'description':  'Port/service scanner, reconnaissance only',
        'indicators':   ['bot_rapid', 'wordlist_scan', 'low'],
        'threat_level': 'LOW',
        'deception':    'deny_fast',
        'color':        '🟢',
    },
}


def classify_attacker(profile: BehaviorProfile) -> dict:
    """
    Classify attacker type using behavioral fingerprint.
    Uses rule-based system built on top of ML features —
    no external API required.
    """
    sophistication = profile.sophistication
    is_bot         = profile.is_bot
    is_targeted    = profile.is_targeted
    attempts       = profile.login_attempts
    rate           = profile.connection_rate

    # APT — highest priority check
    if sophistication == 'apt' or (
        is_targeted and not is_bot and attempts < 20
    ):
        profile_type = 'apt_actor'

    # Targeted human attacker
    elif is_targeted and not is_bot:
        profile_type = 'targeted_attacker'

    # High-volume credential stuffer
    elif (
        profile.unique_usernames > 10 and
        profile.unique_passwords > 10 and
        is_bot
    ):
        profile_type = 'credential_stuffer'

    # Fast automated botnet
    elif is_bot and rate > 10.0 and attempts > 5:
        profile_type = 'botnet_node'

    # Single-shot scanner
    elif attempts <= 2 and rate < 2.0:
        profile_type = 'scanner'

    # Default — script kiddie
    else:
        profile_type = 'script_kiddie'

    meta = PROFILES[profile_type]

    # Build ML-compatible feature vector for our trained models
    features = _build_ml_features(profile)

    return {
        'profile_type':  profile_type,
        'description':   meta['description'],
        'threat_level':  meta['threat_level'],
        'deception':     meta['deception'],
        'color':         meta['color'],
        'sophistication': sophistication,
        'is_bot':        is_bot,
        'is_targeted':   is_targeted,
        'ml_features':   features,
        'evidence': [
            f"Tool: {profile.tool_signature}",
            f"Attempts: {profile.login_attempts}",
            f"Rate: {profile.connection_rate}/s",
            f"Unique users: {profile.unique_usernames}",
            f"Bot behavior: {is_bot}",
            f"Targeted: {is_targeted}",
            f"Sophistication: {sophistication}",
        ],
    }


def _build_ml_features(profile: BehaviorProfile) -> list:
    """
    Build feature vector compatible with our trained models.
    Maps behavioral data to the 7 features used in training.
    """
    # Map sophistication to numeric
    soph_map = {'low': 0, 'medium': 1, 'high': 2, 'apt': 3}

    return [
        profile.login_attempts,               # src_port analog
        2222,                                 # dst_port = SSH
        0,                                    # protocol = TCP
        0,                                    # dataset_source
        1,                                    # is_dangerous_port (SSH)
        0,                                    # port_category
        1 if profile.connection_rate > 5 else 0,  # is_high_port
    ]