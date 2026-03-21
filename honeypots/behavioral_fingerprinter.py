# honeypots/behavioral_fingerprinter.py
"""
Behavioral Fingerprinter — analyzes raw attacker behavior
to extract meaningful signals before ML classification.

Identifies:
- Tool signatures (Hydra, Medusa, Nmap, Metasploit)
- Attack patterns (dictionary, credential stuffing, targeted)
- Timing patterns (bot, human, APT)
- Sophistication level
"""

import re
import time
from dataclasses import dataclass, field


@dataclass
class BehaviorProfile:
    """Complete behavioral fingerprint of one attacker session."""
    # Timing
    connect_time:       float = 0.0
    total_duration:     float = 0.0
    inter_attempt_gaps: list  = field(default_factory=list)

    # Volume
    login_attempts:     int   = 0
    unique_usernames:   int   = 0
    unique_passwords:   int   = 0
    commands_sent:      int   = 0

    # Content
    usernames_tried:    list  = field(default_factory=list)
    passwords_tried:    list  = field(default_factory=list)
    raw_payloads:       list  = field(default_factory=list)

    # Signatures
    tool_signature:     str   = 'unknown'
    protocol_version:   str   = ''
    client_banner:      str   = ''

    # Derived
    is_bot:             bool  = False
    is_targeted:        bool  = False
    sophistication:     str   = 'low'   # low / medium / high / apt
    connection_rate:    float = 1.0


# ── Known tool signatures ──────────────────────────
# These patterns appear in SSH client banners and payloads

TOOL_SIGNATURES = {
    'Hydra':        [b'hydra', b'libssh', b'SSH-2.0-libssh'],
    'Medusa':       [b'medusa', b'SSH-2.0-2.0'],
    'Nmap':         [b'nmap', b'SSH-2.0-OpenSSH_5.3'],
    'Metasploit':   [b'SSH-2.0-Ruby', b'SSH-2.0-Metasploit'],
    'Paramiko':     [b'SSH-2.0-paramiko', b'paramiko'],
    'Masscan':      [b'SSH-2.0-Go', b'SSH-2.0-go'],
    'Custom_Bot':   [b'SSH-2.0-PUTTY', b'SSH-2.0-PuTTY'],
    'Shodan':       [b'SSH-2.0-libssh2'],
}

# Common credential stuffing wordlists signatures
WORDLIST_USERNAMES = {
    'admin', 'root', 'user', 'test', 'guest', 'oracle',
    'ubuntu', 'pi', 'ansible', 'deploy', 'postgres',
    'mysql', 'redis', 'hadoop', 'elasticsearch',
}

APT_USERNAMES = {
    # Targeted — specific to organization types
    'administrator', 'sysadmin', 'backup', 'monitoring',
    'nagios', 'zabbix', 'splunk', 'jenkins', 'gitlab',
}


def detect_tool_signature(banner: bytes) -> str:
    """Identify attack tool from client banner."""
    banner_lower = banner.lower()
    for tool, patterns in TOOL_SIGNATURES.items():
        if any(p.lower() in banner_lower for p in patterns):
            return tool
    return 'Unknown'


def analyze_timing(gaps: list) -> dict:
    """
    Analyze inter-attempt timing to classify bot vs human.

    Bots:    very consistent gaps (< 0.1s variance)
    Human:   irregular gaps (> 0.5s variance)
    APT:     slow deliberate gaps (mean > 2s, low variance)
    """
    if not gaps:
        return {'is_bot': True, 'timing_type': 'single_shot'}

    if len(gaps) < 2:
        mean = gaps[0] if gaps else 1.0
        return {
            'is_bot':      mean < 0.5,
            'timing_type': 'bot_rapid' if mean < 0.5 else 'normal',
            'mean_gap':    mean,
            'variance':    0.0,
        }

    mean     = sum(gaps) / len(gaps)
    variance = sum((g - mean) ** 2 for g in gaps) / len(gaps)
    std_dev  = variance ** 0.5

    if mean < 0.3 and std_dev < 0.1:
        timing_type = 'bot_rapid'
        is_bot      = True
    elif mean < 1.0 and std_dev < 0.3:
        timing_type = 'bot_slow'
        is_bot      = True
    elif mean > 2.0 and std_dev < 0.5:
        timing_type = 'apt_deliberate'
        is_bot      = False
    else:
        timing_type = 'human_manual'
        is_bot      = False

    return {
        'is_bot':      is_bot,
        'timing_type': timing_type,
        'mean_gap':    round(mean, 3),
        'variance':    round(variance, 3),
        'std_dev':     round(std_dev, 3),
    }


def analyze_credentials(
    usernames: list, passwords: list
) -> dict:
    """
    Analyze credential patterns to determine attack type.

    Dictionary attack:    many passwords per username
    Credential stuffing:  many username:password pairs
    Targeted:             specific high-value usernames
    """
    unique_users  = set(u.lower().strip() for u in usernames)
    unique_passes = set(p.strip()         for p in passwords)

    wordlist_hits = unique_users & WORDLIST_USERNAMES
    apt_hits      = unique_users & APT_USERNAMES

    if apt_hits:
        attack_pattern = 'targeted_apt'
        is_targeted    = True
    elif len(unique_users) == 1 and len(unique_passes) > 5:
        attack_pattern = 'dictionary_attack'
        is_targeted    = False
    elif len(unique_users) > 5 and len(unique_passes) > 5:
        attack_pattern = 'credential_stuffing'
        is_targeted    = False
    elif wordlist_hits:
        attack_pattern = 'wordlist_scan'
        is_targeted    = False
    else:
        attack_pattern = 'manual_probe'
        is_targeted    = len(unique_users) <= 2

    return {
        'attack_pattern':  attack_pattern,
        'is_targeted':     is_targeted,
        'unique_users':    len(unique_users),
        'unique_passes':   len(unique_passes),
        'wordlist_hits':   len(wordlist_hits),
        'apt_hits':        len(apt_hits),
    }


def calculate_sophistication(
    tool: str,
    timing: dict,
    creds: dict,
    attempts: int,
) -> str:
    """
    Score overall attacker sophistication.
    Returns: low / medium / high / apt
    """
    score = 0

    # Tool sophistication
    if tool in ('Metasploit', 'Custom_Bot'):
        score += 3
    elif tool in ('Hydra', 'Medusa', 'Paramiko'):
        score += 2
    elif tool != 'Unknown':
        score += 1

    # Timing sophistication
    if timing.get('timing_type') == 'apt_deliberate':
        score += 4
    elif timing.get('timing_type') == 'human_manual':
        score += 2
    elif timing.get('timing_type') == 'bot_slow':
        score += 1

    # Credential sophistication
    if creds.get('attack_pattern') == 'targeted_apt':
        score += 4
    elif creds.get('attack_pattern') == 'manual_probe':
        score += 3
    elif creds.get('attack_pattern') == 'credential_stuffing':
        score += 2

    # Volume
    if attempts > 100:
        score += 2
    elif attempts > 20:
        score += 1

    if score >= 9:
        return 'apt'
    elif score >= 6:
        return 'high'
    elif score >= 3:
        return 'medium'
    else:
        return 'low'


def build_fingerprint(
    client_banner: bytes,
    payloads:      list,
    timestamps:    list,
    usernames:     list,
    passwords:     list,
    source_ip:     str,
) -> BehaviorProfile:
    """
    Build complete behavioral fingerprint from session data.
    Called after session ends or times out.
    """
    profile = BehaviorProfile()

    profile.client_banner   = client_banner.decode('utf-8', errors='replace')
    profile.raw_payloads    = [p.hex() for p in payloads[:20]]
    profile.usernames_tried = usernames[:50]
    profile.passwords_tried = passwords[:50]
    profile.login_attempts  = len(usernames)
    profile.unique_usernames = len(set(usernames))
    profile.unique_passwords = len(set(passwords))

    # Timing analysis
    if len(timestamps) >= 2:
        gaps = [
            timestamps[i+1] - timestamps[i]
            for i in range(len(timestamps) - 1)
        ]
        profile.inter_attempt_gaps = gaps
        timing = analyze_timing(gaps)
        profile.is_bot = timing['is_bot']
        profile.connection_rate = round(
            len(timestamps) / max(
                timestamps[-1] - timestamps[0], 0.001
            ), 2
        )
    else:
        profile.is_bot          = True
        profile.connection_rate = 1.0

    # Tool detection
    profile.tool_signature = detect_tool_signature(client_banner)
    for payload in payloads:
        sig = detect_tool_signature(payload)
        if sig != 'Unknown':
            profile.tool_signature = sig
            break

    # Credential analysis
    creds = analyze_credentials(usernames, passwords)
    profile.is_targeted = creds['is_targeted']

    # Timing
    timing = analyze_timing(profile.inter_attempt_gaps)

    # Sophistication
    profile.sophistication = calculate_sophistication(
        tool     = profile.tool_signature,
        timing   = timing,
        creds    = creds,
        attempts = profile.login_attempts,
    )

    return profile