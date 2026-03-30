# honeypots/ssh_honeypot.py
"""
HoneyCloud Sentinel — Adaptive SSH Honeypot
Phase B: Full behavioral analysis + adaptive deception

Upgrade from basic socket → full behavioral intelligence:
  - Multi-round credential collection
  - Behavioral fingerprinting
  - ML-based attacker profiling
  - Adaptive deception (4 strategies)
  - Rich telemetry to Kafka
"""

import socket
import threading
import json
import time
import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from kafka import KafkaProducer
from honeypots.behavioral_fingerprinter import build_fingerprint
from honeypots.attacker_profiler        import classify_attacker
from honeypots.adaptive_response        import select_and_execute

# ── Config ─────────────────────────────────────────
PORT             = 2222
MAX_CONNECTIONS  = 200
SESSION_TIMEOUT  = 30    # seconds before closing idle session
MAX_ATTEMPTS     = 50    # max login attempts to collect
LOG_FILE         = 'logs/ssh_adaptive.json'

os.makedirs('logs', exist_ok=True)

# ── Kafka ───────────────────────────────────────────
# try:
#     producer = KafkaProducer(
#         bootstrap_servers=['localhost:9092'],
#         value_serializer=lambda v: json.dumps(v).encode('utf-8'),
#         retries=3,
#     )
#     print('[✓] Kafka connected')
# except Exception as e:
#     print(f'[!] Kafka unavailable: {e} — logging to file only')
#     producer = None

# ── Kafka ───────────────────────────────────────────
def _create_producer():
    """
    Create KafkaProducer.
    Uses Redpanda Cloud (SASL_SSL) if env vars present,
    falls back to local Docker Kafka for development.
    """
    import ssl
    from dotenv import load_dotenv
    load_dotenv()

    BROKER   = os.getenv('REDPANDA_BROKER',   '').strip()
    USERNAME = os.getenv('REDPANDA_USERNAME',  '').strip()
    PASSWORD = os.getenv('REDPANDA_PASSWORD',  '').strip()

    if BROKER and USERNAME and PASSWORD:
        ssl_ctx = ssl.create_default_context()
        p = KafkaProducer(
            bootstrap_servers   = [BROKER],
            security_protocol   = 'SASL_SSL',
            sasl_mechanism      = 'SCRAM-SHA-256',
            sasl_plain_username = USERNAME,
            sasl_plain_password = PASSWORD,
            ssl_context         = ssl_ctx,
            value_serializer    = lambda v: json.dumps(v).encode('utf-8'),
            retries             = 5,
            request_timeout_ms  = 30000,
        )
        print(f'[✓] Redpanda Cloud connected → {BROKER}')
        return p
    else:
        p = KafkaProducer(
            bootstrap_servers = ['localhost:9092'],
            value_serializer  = lambda v: json.dumps(v).encode('utf-8'),
            retries           = 3,
        )
        print('[✓] Local Kafka connected')
        return p

try:
    producer = _create_producer()
except Exception as e:
    print(f'[!] Kafka unavailable: {e} — logging to file only')
    producer = None

# def get_kafka_producer():
#     import ssl
#     from kafka import KafkaProducer

#     BROKER   = os.getenv('UPSTASH_KAFKA_BROKER',   '')
#     USERNAME = os.getenv('UPSTASH_KAFKA_USERNAME',  '')
#     PASSWORD = os.getenv('UPSTASH_KAFKA_PASSWORD',  '')

#     if BROKER:
#         return KafkaProducer(
#             bootstrap_servers   = [BROKER],
#             security_protocol   = 'SASL_SSL',
#             sasl_mechanism      = 'SCRAM-SHA-256',
#             sasl_plain_username = USERNAME,
#             sasl_plain_password = PASSWORD,
#             ssl_context         = ssl.create_default_context(),
#             value_serializer    = lambda v: json.dumps(v).encode('utf-8'),
#         )
#     else:
#         return KafkaProducer(
#             bootstrap_servers = ['localhost:9092'],
#             value_serializer  = lambda v: json.dumps(v).encode('utf-8'),
#         )


# ── Session handler ─────────────────────────────────

def handle_client(conn, addr):
    """
    Full adaptive session handler.
    Collects behavioral data → profiles attacker →
    selects deception strategy → sends rich telemetry.
    """
    source_ip   = addr[0]
    source_port = addr[1]
    session_start = time.time()

    print(f"\n[+] Connection from {source_ip}:{source_port}")

    # ── Phase 1: Initial data collection ──────────────
    payloads   = []
    usernames  = []
    passwords  = []
    timestamps = []
    client_banner = b''

    try:
        conn.settimeout(SESSION_TIMEOUT)

        # Send SSH banner
        conn.send(b'SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n')

        # Collect initial client banner
        try:
            client_banner = conn.recv(256) or b''
            if client_banner:
                payloads.append(client_banner)
                timestamps.append(time.time())
        except Exception:
            pass

        # Collect credential attempts
        # Send fake auth challenge repeatedly
        for attempt in range(MAX_ATTEMPTS):
            try:
                # Fake password prompt
                conn.send(
                    f'{source_ip}\'s password: '.encode()
                )
                data = conn.recv(256)
                if not data:
                    break

                timestamps.append(time.time())
                payloads.append(data)

                # Parse username:password if colon-separated
                decoded = data.strip().decode('utf-8', errors='replace')
                if ':' in decoded:
                    parts = decoded.split(':', 1)
                    usernames.append(parts[0])
                    passwords.append(parts[1])
                else:
                    passwords.append(decoded)
                    # Default username guesses
                    usernames.append(
                        ['root','admin','user','ubuntu','pi']
                        [attempt % 5]
                    )

                # Send rejection to keep them trying
                if attempt < MAX_ATTEMPTS - 1:
                    conn.send(
                        b'Permission denied, please try again.\r\n'
                    )

            except socket.timeout:
                break
            except Exception:
                break

    except Exception as e:
        print(f'[!] Collection phase error: {e}')

    # ── Phase 2: Behavioral fingerprinting ────────────
    profile = build_fingerprint(
        client_banner = client_banner,
        payloads      = payloads,
        timestamps    = timestamps,
        usernames     = usernames,
        passwords     = passwords,
        source_ip     = source_ip,
    )

    # ── Phase 3: Attacker classification ──────────────
    classification = classify_attacker(profile)

    print(
        f"[Profile] {source_ip} → "
        f"{classification['color']} "
        f"{classification['profile_type']} "
        f"({classification['threat_level']}) "
        f"strategy={classification['deception']}"
    )

    # ── Phase 4: Adaptive deception ───────────────────
    interaction = select_and_execute(
        conn                = conn,
        deception_strategy  = classification['deception'],
        profile_type        = classification['profile_type'],
    )

    # ── Phase 5: Build rich telemetry ─────────────────
    session_duration = round(time.time() - session_start, 2)

    log = {
        # Standard fields (compatible with existing ML pipeline)
        'timestamp':      time.strftime('%Y-%m-%d %H:%M:%S'),
        'source_ip':      source_ip,
        'source_port':    source_port,
        'port_targeted':  PORT,
        'protocol':       'SSH',
        'login_attempts': profile.login_attempts or 1,
        'connection_rate': profile.connection_rate,
        'data_hex':       payloads[0].hex() if payloads else '',

        # Behavioral intelligence (NEW)
        'behavioral': {
            'tool_signature':   profile.tool_signature,
            'client_banner':    profile.client_banner[:100],
            'is_bot':           profile.is_bot,
            'is_targeted':      profile.is_targeted,
            'sophistication':   profile.sophistication,
            'unique_usernames': profile.unique_usernames,
            'unique_passwords': profile.unique_passwords,
            'session_duration': session_duration,
            'usernames_sample': profile.usernames_tried[:5],
            'passwords_sample': [
                '***' for _ in profile.passwords_tried[:5]
            ],
        },

        # Attacker profile (NEW)
        'attacker_profile': {
            'type':        classification['profile_type'],
            'description': classification['description'],
            'threat_level': classification['threat_level'],
            'evidence':    classification['evidence'],
        },

        # Deception result (NEW)
        'deception': {
            'strategy':        interaction['strategy'],
            'interaction':     interaction['interaction'],
            'intel_collected': interaction['intel_collected'],
            'commands':        interaction.get('commands', []),
            'honeytoken_hit':  bool(
                interaction.get('honeytoken_accessed')
            ),
        },
    }

    # ── Phase 6: Send to Kafka + log to file ──────────
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(log) + '\n')
    except Exception as e:
        print(f'[!] Log write error: {e}')

    if producer:
        try:
            producer.send('honeypot-attacks', log)
            producer.flush()
            print(
                f"[Kafka] Sent: {classification['profile_type']} "
                f"from {source_ip} "
                f"({profile.login_attempts} attempts, "
                f"{len(interaction.get('commands', []))} cmds)"
            )
        except Exception as e:
            print(f'[!] Kafka send error: {e}')

    conn.close()


# ── Server ──────────────────────────────────────────

def run():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORT))
    server.listen(MAX_CONNECTIONS)

    print(f'\n{"="*55}')
    print(f'  HoneyCloud Sentinel — Adaptive SSH Honeypot')
    print(f'{"="*55}')
    print(f'  Port:      {PORT}')
    print(f'  Strategies: deny_fast | slow_response | '
          f'fake_success | full_fake_env')
    
    # print(f'  Kafka:     {"connected" if producer else "offline"}')
    # import os
    _broker = os.getenv('REDPANDA_BROKER', 'localhost:9092')
    print(f'  Kafka:     {"connected" if producer else "offline"} ({_broker})')
    print(f'  Log file:  {LOG_FILE}')
    print(f'{"="*55}\n')

    while True:
        try:
            conn, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            ).start()
        except KeyboardInterrupt:
            print('\n[!] Honeypot stopped')
            server.close()
            break
        except Exception as e:
            print(f'[!] Accept error: {e}')


if __name__ == '__main__':
    run()