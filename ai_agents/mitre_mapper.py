# ai_agents/mitre_mapper.py

# Full MITRE ATT&CK mapping for honeypot attack types
# Source: https://attack.mitre.org

MITRE_DATABASE = {

    # ── SSH Brute Force ────────────────────────────────────────────
    'SSH Brute Force': {
        'technique_id':   'T1110.001',
        'technique_name': 'Brute Force: Password Guessing',
        'tactic':         'Credential Access',
        'tactic_id':      'TA0006',
        'description':    (
            'Adversaries attempt to gain access to accounts by '
            'systematically guessing passwords against SSH services. '
            'This is one of the most common initial access techniques '
            'targeting internet-exposed systems.'
        ),
        'detection':      (
            'Monitor for repeated failed authentication attempts. '
            'Alert on >10 failed logins per minute from a single IP.'
        ),
        'mitigation':     [
            'M1036 — Account Use Policies: enforce lockout after failed attempts',
            'M1032 — Multi-factor Authentication: require MFA for SSH',
            'M1027 — Password Policies: enforce strong password requirements',
            'Restrict SSH access to known IP ranges via firewall rules',
        ],
        'severity':       'HIGH',
        'color':          '#ff6b00',
        'url':            'https://attack.mitre.org/techniques/T1110/001/',
    },

    # ── Web Exploit ────────────────────────────────────────────────
    'Web Exploit': {
        'technique_id':   'T1190',
        'technique_name': 'Exploit Public-Facing Application',
        'tactic':         'Initial Access',
        'tactic_id':      'TA0001',
        'description':    (
            'Adversaries attempt to exploit weaknesses in internet-facing '
            'web applications. This includes SQL injection, XSS, RFI, '
            'and exploitation of known CVEs in web frameworks.'
        ),
        'detection':      (
            'Monitor web server logs for unusual request patterns, '
            'SQL keywords in URLs, and error spikes.'
        ),
        'mitigation':     [
            'M1048 — Application Isolation: use WAF to filter malicious requests',
            'M1030 — Network Segmentation: isolate web servers',
            'M1016 — Vulnerability Scanning: patch known CVEs promptly',
            'Input validation and parameterized queries for all user input',
        ],
        'severity':       'CRITICAL',
        'color':          '#ff2d2d',
        'url':            'https://attack.mitre.org/techniques/T1190/',
    },

    # ── Database Attack ────────────────────────────────────────────
    'Database Attack': {
        'technique_id':   'T1078.001',
        'technique_name': 'Valid Accounts: Default Accounts',
        'tactic':         'Persistence',
        'tactic_id':      'TA0003',
        'description':    (
            'Adversaries attempt to access database services using '
            'default credentials or brute-forced passwords. Successful '
            'access can lead to full data exfiltration or ransomware deployment.'
        ),
        'detection':      (
            'Alert on database login attempts from external IPs. '
            'Monitor for bulk SELECT or DROP TABLE statements.'
        ),
        'mitigation':     [
            'M1026 — Privileged Account Management: disable default DB accounts',
            'M1035 — Limit Access to Resource over Network: firewall DB ports',
            'M1027 — Password Policies: enforce strong DB passwords',
            'Never expose database ports (3306, 5432, 27017) to internet',
        ],
        'severity':       'CRITICAL',
        'color':          '#ff2d2d',
        'url':            'https://attack.mitre.org/techniques/T1078/001/',
    },

    # ── FTP Attack ─────────────────────────────────────────────────
    'FTP Attack': {
        'technique_id':   'T1071.002',
        'technique_name': 'Application Layer Protocol: File Transfer',
        'tactic':         'Command and Control',
        'tactic_id':      'TA0011',
        'description':    (
            'Adversaries use FTP to transfer malware, exfiltrate data, '
            'or establish a command-and-control channel. FTP transmits '
            'credentials in plaintext making it easily interceptable.'
        ),
        'detection':      (
            'Monitor FTP traffic for anonymous login attempts '
            'and large file transfers to unknown destinations.'
        ),
        'mitigation':     [
            'M1031 — Network Intrusion Prevention: block suspicious FTP traffic',
            'Replace FTP with SFTP or FTPS for encrypted transfers',
            'M1035 — Limit Access: restrict FTP to authorized hosts only',
            'Disable anonymous FTP access entirely',
        ],
        'severity':       'HIGH',
        'color':          '#ff6b00',
        'url':            'https://attack.mitre.org/techniques/T1071/002/',
    },

    # ── Port Scan ──────────────────────────────────────────────────
    'Port Scan / Other': {
        'technique_id':   'T1046',
        'technique_name': 'Network Service Discovery',
        'tactic':         'Discovery',
        'tactic_id':      'TA0007',
        'description':    (
            'Adversaries scan networks to enumerate running services '
            'and identify potential targets. Port scanning is typically '
            'a precursor to more targeted exploitation attempts.'
        ),
        'detection':      (
            'Alert on high-rate connection attempts across multiple ports '
            'from a single source within a short time window.'
        ),
        'mitigation':     [
            'M1030 — Network Segmentation: limit which systems are reachable',
            'M1031 — Network Intrusion Prevention: detect and block scan patterns',
            'Implement rate limiting on connection attempts per IP',
            'Use port knocking or non-standard ports for sensitive services',
        ],
        'severity':       'MEDIUM',
        'color':          '#ffe600',
        'url':            'https://attack.mitre.org/techniques/T1046/',
    },

    # ── Telnet Attack ──────────────────────────────────────────────
    'Telnet Attack': {
        'technique_id':   'T1021.004',
        'technique_name': 'Remote Services: SSH / Telnet',
        'tactic':         'Lateral Movement',
        'tactic_id':      'TA0008',
        'description':    (
            'Adversaries exploit Telnet services which transmit all data '
            'including credentials in plaintext. Telnet is heavily targeted '
            'by IoT botnets such as Mirai for credential harvesting.'
        ),
        'detection':      (
            'Alert on any Telnet traffic — this protocol should not be '
            'in use in modern infrastructure.'
        ),
        'mitigation':     [
            'Disable Telnet entirely — replace with SSH',
            'M1042 — Disable or Remove Feature: remove Telnet daemon',
            'Block port 23 at the firewall level',
            'Change default credentials on all IoT devices immediately',
        ],
        'severity':       'CRITICAL',
        'color':          '#ff2d2d',
        'url':            'https://attack.mitre.org/techniques/T1021/004/',
        
    
    },
    # Add these 3 entries to MITRE_DATABASE in ai_agents/mitre_mapper.py

    # ── SMB Attack ─────────────────────────────────────────────────
    'SMB Attack': {
        'technique_id':   'T1021.002',
        'technique_name': 'Remote Services: SMB/Windows Admin Shares',
        'tactic':         'Lateral Movement',
        'tactic_id':      'TA0008',
        'description':    (
            'Adversaries exploit SMB protocol to move laterally across '
            'networks, access file shares, or deploy malware. SMB '
            'vulnerabilities like EternalBlue (MS17-010) have been used '
            'by ransomware families including WannaCry and NotPetya for '
            'devastating large-scale attacks.'
        ),
        'detection':      (
            'Monitor SMB traffic on ports 445 and 139. Alert on '
            'authentication failures and unusual file access patterns. '
            'Block SMB at perimeter — it should never be internet-facing.'
        ),
        'mitigation':     [
            'M1042 — Disable or Remove Feature: block SMB at firewall',
            'MS17-010 patch — apply immediately if not already done',
            'M1037 — Filter Network Traffic: block ports 445 and 139',
            'M1026 — Privileged Account Management: limit admin shares',
        ],
        'severity':       'CRITICAL',
        'color':          '#ff2d2d',
        'url':            'https://attack.mitre.org/techniques/T1021/002/',
    },

    # ── Email Attack ───────────────────────────────────────────────
    'Email Attack': {
        'technique_id':   'T1566.001',
        'technique_name': 'Phishing: Spearphishing Attachment',
        'tactic':         'Initial Access',
        'tactic_id':      'TA0001',
        'description':    (
            'Adversaries probe email services (SMTP port 25, 587, 465) '
            'for open relays, credential harvesting, or as staging '
            'infrastructure for phishing campaigns. Open SMTP relays '
            'are exploited to send spam and malware at scale.'
        ),
        'detection':      (
            'Monitor SMTP connection attempts from external IPs. '
            'Alert on authentication failures and relay attempts. '
            'Check for unusual sending volumes from single sources.'
        ),
        'mitigation':     [
            'M1054 — Software Configuration: disable open mail relay',
            'M1017 — User Training: educate users on phishing',
            'Implement SPF, DKIM, and DMARC email authentication',
            'M1031 — Network Intrusion Prevention: filter SMTP traffic',
        ],
        'severity':       'HIGH',
        'color':          '#ff6b00',
        'url':            'https://attack.mitre.org/techniques/T1566/001/',
    },

    # ── DNS Attack ─────────────────────────────────────────────────
    'DNS Attack': {
        'technique_id':   'T1071.004',
        'technique_name': 'Application Layer Protocol: DNS',
        'tactic':         'Command and Control',
        'tactic_id':      'TA0011',
        'description':    (
            'Adversaries abuse DNS protocol for command-and-control '
            'communication, data exfiltration via DNS tunneling, or '
            'amplification DDoS attacks. DNS traffic is often allowed '
            'through firewalls making it an attractive covert channel.'
        ),
        'detection':      (
            'Monitor for unusually high DNS query volumes from single '
            'sources. Alert on DNS queries with abnormally long names '
            'or high entropy subdomains indicating tunneling.'
        ),
        'mitigation':     [
            'M1037 — Filter Network Traffic: restrict DNS to trusted resolvers',
            'M1031 — Network Intrusion Prevention: detect DNS tunneling',
            'Deploy DNS monitoring and anomaly detection',
            'Block recursive DNS queries from external sources',
        ],
        'severity':       'MEDIUM',
        'color':          '#ffe600',
        'url':            'https://attack.mitre.org/techniques/T1071/004/',
    },
}

# MITRE Tactic ordering (kill chain order)
TACTIC_ORDER = [
    'TA0001',  # Initial Access
    'TA0002',  # Execution
    'TA0003',  # Persistence
    'TA0004',  # Privilege Escalation
    'TA0005',  # Defense Evasion
    'TA0006',  # Credential Access
    'TA0007',  # Discovery
    'TA0008',  # Lateral Movement
    'TA0009',  # Collection
    'TA0010',  # Exfiltration
    'TA0011',  # Command and Control
    'TA0040',  # Impact
]

TACTIC_NAMES = {
    'TA0001': 'Initial Access',
    'TA0002': 'Execution',
    'TA0003': 'Persistence',
    'TA0004': 'Privilege Escalation',
    'TA0005': 'Defense Evasion',
    'TA0006': 'Credential Access',
    'TA0007': 'Discovery',
    'TA0008': 'Lateral Movement',
    'TA0009': 'Collection',
    'TA0010': 'Exfiltration',
    'TA0011': 'Command & Control',
    'TA0040': 'Impact',
}


def map_attack_to_mitre(attack_type: str) -> dict:
    """
    Maps an attack type string to its MITRE ATT&CK entry.
    Returns a default entry if not found.
    """
    entry = MITRE_DATABASE.get(attack_type)

    if entry:
        return {
            'technique_id':   entry['technique_id'],
            'technique_name': entry['technique_name'],
            'tactic':         entry['tactic'],
            'tactic_id':      entry['tactic_id'],
            'severity':       entry['severity'],
            'color':          entry['color'],
            'url':            entry['url'],
            'mitre_mapped':   True,
        }

    # Default for unknown attack types
    return {
        'technique_id':   'T1499',
        'technique_name': 'Endpoint Denial of Service',
        'tactic':         'Impact',
        'tactic_id':      'TA0040',
        'severity':       'MEDIUM',
        'color':          '#ffe600',
        'url':            'https://attack.mitre.org/techniques/T1499/',
        'mitre_mapped':   False,
    }


def get_mitre_detail(attack_type: str) -> dict:
    """Returns full MITRE detail including mitigations."""
    return MITRE_DATABASE.get(attack_type, {})


def build_heatmap_data(attacks: list) -> list:
    """
    Builds tactic frequency data for the ATT&CK heatmap.
    Returns list of {tactic_id, tactic_name, count, techniques} 
    sorted by kill chain order.
    """
    tactic_counts    = {}
    tactic_techniques = {}

    for attack in attacks:
        attack_type = attack.get('attack_type', 'Unknown')
        entry = MITRE_DATABASE.get(attack_type)
        if not entry:
            continue

        tid  = entry['tactic_id']
        tech = entry['technique_id']

        tactic_counts[tid] = tactic_counts.get(tid, 0) + 1

        if tid not in tactic_techniques:
            tactic_techniques[tid] = {}
        tactic_techniques[tid][tech] = (
            tactic_techniques[tid].get(tech, 0) + 1
        )

    result = []
    for tid in TACTIC_ORDER:
        if tid in tactic_counts:
            techs = tactic_techniques.get(tid, {})
            result.append({
                'tactic_id':   tid,
                'tactic_name': TACTIC_NAMES.get(tid, tid),
                'count':       tactic_counts[tid],
                'techniques':  [
                    {'id': k, 'count': v}
                    for k, v in sorted(
                        techs.items(), key=lambda x: x[1], reverse=True
                    )
                ],
            })

    return result