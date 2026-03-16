# Phase 1: Slow trickle     (3 attacks, builds suspense)
# Phase 2: Botnet wave      (20 attacks from same campaign)
# Phase 3: APT scenario     (targeted, stealthy, high risk)
# Phase 4: Attack flood     (rapid fire, dashboard goes crazy)
# Phase 5: Critical alert   (one devastating attack to end on)

# scripts/demo.py
import json
import time
import random
import datetime
from kafka import KafkaProducer

# ── Setup ──────────────────────────────────────────────
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send(log: dict):
    producer.send('honeypot-attacks', log)
    producer.flush()

def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def banner(text: str, color: str = '\033[96m'):
    reset = '\033[0m'
    bold  = '\033[1m'
    width = 54
    print(f"\n{color}{bold}{'─' * width}")
    print(f"  {text}")
    print(f"{'─' * width}{reset}\n")

def log_sent(attack_type: str, ip: str, port: int, risk: str):
    colors = {
        'CRITICAL': '\033[91m',   # red
        'HIGH':     '\033[93m',   # yellow
        'MEDIUM':   '\033[33m',   # orange
        'LOW':      '\033[94m',   # blue
    }
    reset = '\033[0m'
    color = colors.get(risk, reset)
    print(f"  {color}[{risk}]{reset}  {attack_type:<25}  {ip:<18}  :{port}")
    time.sleep(0.05)

# ── Attack Templates ───────────────────────────────────

def make_ssh_brute(ip: str, attempts: int = None) -> dict:
    return {
        'source_ip':      ip,
        'source_port':    random.randint(40000, 65000),
        'port_targeted':  22,
        'protocol':       'tcp',
        'country':        random.choice(['Russia', 'China', 'Romania', 'Ukraine', 'Brazil']),
        'login_attempts': attempts or random.randint(50, 500),
        'connection_rate': round(random.uniform(10, 50), 2),
        'timestamp':      now(),
    }

def make_web_exploit(ip: str) -> dict:
    return {
        'source_ip':      ip,
        'source_port':    random.randint(40000, 65000),
        'port_targeted':  random.choice([80, 8080, 443]),
        'protocol':       'tcp',
        'country':        random.choice(['China', 'USA', 'Germany', 'Netherlands', 'India']),
        'login_attempts': 1,
        'connection_rate': round(random.uniform(1, 10), 2),
        'timestamp':      now(),
    }

def make_db_attack(ip: str) -> dict:
    return {
        'source_ip':      ip,
        'source_port':    random.randint(40000, 65000),
        'port_targeted':  random.choice([3306, 5432, 27017, 6379]),
        'protocol':       'tcp',
        'country':        random.choice(['North Korea', 'China', 'Iran', 'Russia']),
        'login_attempts': random.randint(10, 100),
        'connection_rate': round(random.uniform(5, 30), 2),
        'timestamp':      now(),
    }

def make_port_scan(ip: str) -> dict:
    return {
        'source_ip':      ip,
        'source_port':    random.randint(40000, 65000),
        'port_targeted':  random.choice([21, 23, 25, 53, 110, 143, 389, 8080, 8443]),
        'protocol':       'tcp',
        'country':        random.choice(['Netherlands', 'USA', 'France', 'UK', 'Singapore']),
        'login_attempts': 1,
        'connection_rate': round(random.uniform(20, 100), 2),
        'timestamp':      now(),
    }

def make_ftp_attack(ip: str) -> dict:
    return {
        'source_ip':      ip,
        'source_port':    random.randint(40000, 65000),
        'port_targeted':  21,
        'protocol':       'tcp',
        'country':        random.choice(['Brazil', 'Indonesia', 'Vietnam', 'Pakistan']),
        'login_attempts': random.randint(20, 200),
        'connection_rate': round(random.uniform(5, 25), 2),
        'timestamp':      now(),
    }

def make_normal_noise(ip: str) -> dict:
    """Very low intensity traffic that should appear as LOW risk."""
    return {
        'source_ip': ip,
        'source_port': random.randint(40000, 65000),
        'port_targeted': random.choice([80, 443, 53]),
        'protocol': 'tcp',
        'country': random.choice(['USA', 'Germany', 'France', 'UK', 'Singapore']),
        'login_attempts': 1,
        'connection_rate': round(random.uniform(0.2, 2.0), 2),
        'timestamp': now(),
    }
# ── Demo Phases ────────────────────────────────────────

def phase_0_background():
    """Normal internet background noise."""
    banner("PHASE 0  ›  BACKGROUND INTERNET TRAFFIC", '\033[92m')
    print("  Normal internet scanning and harmless connections...\n")

    for _ in range(8):
        ip = f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'
        log = make_normal_noise(ip)
        send(log)
        log_sent('Background Traffic', ip, log['port_targeted'], 'LOW')
        time.sleep(0.7)

    print("\n  [Dashboard] LOW risk baseline established...")
    time.sleep(2)

def phase_1_trickle():
    """3 slow attacks to establish baseline — builds suspense."""
    banner("PHASE 1  ›  INITIAL RECONNAISSANCE DETECTED", '\033[94m')
    print("  Slow, deliberate probing from unknown sources...\n")

    attacks = [
        (make_port_scan('45.33.32.156'),   'LOW'),
        (make_port_scan('192.241.179.23'), 'LOW'),
        (make_ssh_brute('185.220.101.45', 12), 'MEDIUM'),
    ]

    for log, risk in attacks:
        send(log)
        log_sent('Reconnaissance', log['source_ip'], log['port_targeted'], risk)
        time.sleep(2)

    print("\n  [Dashboard] Watch the MEDIUM counter tick up...")
    time.sleep(3)


def phase_2_botnet():
    """20 attacks from the same /24 subnet — clearly a botnet."""
    banner("PHASE 2  ›  BOTNET CAMPAIGN IDENTIFIED", '\033[93m')
    print("  20 hosts from same network — coordinated botnet attack!\n")

    # All from same /24 — clear botnet signature
    base_ip = '91.240.118'
    for i in range(20):
        ip  = f'{base_ip}.{random.randint(1, 254)}'
        log = make_ssh_brute(ip, random.randint(100, 300))
        send(log)
        log_sent('SSH Brute Force', ip, 22, 'HIGH')
        time.sleep(0.4)

    print("\n  [Dashboard] HIGH counter climbing — campaign detected!")
    time.sleep(3)


def phase_3_apt():
    """Slow, targeted APT-style attack — high sophistication."""
    banner("PHASE 3  ›  APT INTRUSION SCENARIO", '\033[91m')
    print("  Advanced Persistent Threat — slow, targeted, dangerous.\n")

    apt_ip = '203.0.113.42'

    # Step 1: quiet recon
    print("  [APT Step 1] Silent port scan...")
    send(make_port_scan(apt_ip))
    log_sent('Port Scan', apt_ip, 443, 'LOW')
    time.sleep(3)

    # Step 2: web exploit probe
    print("\n  [APT Step 2] Web vulnerability probe...")
    for _ in range(3):
        send(make_web_exploit(apt_ip))
        log_sent('Web Exploit Probe', apt_ip, 80, 'MEDIUM')
        time.sleep(1.5)

    # Step 3: database access attempt
    print("\n  [APT Step 3] Database access attempt...")
    for _ in range(2):
        send(make_db_attack(apt_ip))
        log_sent('Database Attack', apt_ip, 3306, 'CRITICAL')
        time.sleep(2)

    print("\n  [Dashboard] Same IP across all attack types — ANOMALY FLAG!")
    time.sleep(4)


def phase_4_flood():
    """Rapid fire mixed attacks — dashboard goes into overdrive."""
    banner("PHASE 4  ›  MASS ATTACK FLOOD", '\033[91m')
    print("  40 mixed attacks — multiple vectors simultaneously!\n")

    attack_factories = [
        lambda: make_ssh_brute(f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'),
        lambda: make_web_exploit(f'{random.randint(1,255)}.{random.randint(1,255)}.0.1'),
        lambda: make_db_attack(f'10.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'),
        lambda: make_port_scan(f'{random.randint(1,255)}.{random.randint(1,255)}.1.1'),
        lambda: make_ftp_attack(f'{random.randint(1,255)}.{random.randint(1,255)}.0.{random.randint(1,255)}'),
    ]

    risk_cycle = ['HIGH', 'CRITICAL', 'HIGH', 'MEDIUM', 'CRITICAL',
                  'HIGH', 'HIGH', 'CRITICAL', 'MEDIUM', 'HIGH']

    for i in range(40):
        factory = random.choice(attack_factories)
        log     = factory()
        risk    = risk_cycle[i % len(risk_cycle)]
        send(log)
        log_sent('Mixed Attack', log['source_ip'], log['port_targeted'], risk)
        time.sleep(0.15)   # fast — 40 attacks in ~6 seconds

    print("\n  [Dashboard] Feed scrolling fast — charts updating!")
    time.sleep(3)


def phase_5_critical():
    """One devastating final attack — ends on a high note."""
    banner("PHASE 5  ›  CRITICAL THREAT — DATABASE BREACH ATTEMPT", '\033[91m')
    print("  Coordinated database exfiltration attempt detected.\n")

    # Three IPs all hitting the database simultaneously
    ips = ['185.220.101.12', '185.220.101.89', '185.220.101.234']
    print("  Simultaneous hits from 3 IPs on port 27017 (MongoDB)...\n")

    for ip in ips:
        log = {
            'source_ip':       ip,
            'source_port':     random.randint(40000, 65000),
            'port_targeted':   27017,
            'protocol':        'tcp',
            'country':         'Russia',
            'login_attempts':  random.randint(200, 500),
            'connection_rate': round(random.uniform(40, 80), 2),
            'timestamp':       now(),
        }
        send(log)
        log_sent('MongoDB Attack', ip, 27017, 'CRITICAL')
        time.sleep(0.8)

    print("\n  [Dashboard] 3x CRITICAL — risk score maxed out!")


# ── Main Entry ─────────────────────────────────────────

def run_full_demo():
    print("""
\033[96m\033[1m
╔══════════════════════════════════════════════════════╗
║          HONEYCLOUD SENTINEL — LIVE DEMO             ║
║          Make sure dashboard is open first!          ║
╚══════════════════════════════════════════════════════╝
\033[0m
  Open:  http://localhost:3000
  Then press ENTER to start the demo...
    """)
    input()
    phase_0_background()
    phase_1_trickle()
    phase_2_botnet()
    phase_3_apt()
    phase_4_flood()
    phase_5_critical()

    print("""
\033[92m\033[1m
╔══════════════════════════════════════════════════════╗
║                  DEMO COMPLETE ✓                     ║
║                                                      ║
║   Total attacks sent: ~66                            ║
║   Check dashboard for live stats                     ║
╚══════════════════════════════════════════════════════╝
\033[0m""")


def run_quick_demo():
    """Shorter 30-second version — if you have limited time."""
    banner("HONEYCLOUD — QUICK DEMO (30 seconds)", '\033[96m')

    # 5 varied attacks quickly
    attacks = [
        make_port_scan('45.33.32.156'),
        make_ssh_brute('91.240.118.45', 250),
        make_web_exploit('103.27.186.5'),
        make_db_attack('185.234.219.4'),
        make_db_attack('185.234.219.5'),
    ]
    labels = ['Port Scan', 'SSH Brute Force', 'Web Exploit',
              'Database Attack', 'Database Attack']
    risks  = ['LOW', 'HIGH', 'MEDIUM', 'CRITICAL', 'CRITICAL']

    for log, label, risk in zip(attacks, labels, risks):
        send(log)
        log_sent(label, log['source_ip'], log['port_targeted'], risk)
        time.sleep(1)

    print("\n  Done! Check http://localhost:3000\n")


if __name__ == '__main__':
    import sys
    if '--quick' in sys.argv:
        run_quick_demo()
    else:
        run_full_demo()