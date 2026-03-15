# honeypots/ssh_honeypot.py
import socket
import threading
import json
import datetime
from kafka import KafkaProducer

# Connect to Kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def handle_client(conn, addr):
    try:
        # Send fake SSH banner so attacker thinks it's real
        conn.send(b'SSH-2.0-OpenSSH_8.9\r\n')
        data = conn.recv(1024)

        # Build the attack log
        log = {
            'timestamp': str(datetime.datetime.now()),
            'source_ip': addr[0],
            'source_port': addr[1],
            'port_targeted': 2222,
            'protocol': 'SSH',
            'data_hex': data.hex() if data else '',
            'login_attempts': 1,
            'connection_rate': 1.0
        }

        # Save to file (backup)
        with open('logs/ssh_attacks.json', 'a') as f:
            f.write(json.dumps(log) + '\n')

        # Send to Kafka
        producer.send('honeypot-attacks', log)
        producer.flush()

        print(f"[+] Attack from {addr[0]}:{addr[1]} → sent to Kafka")

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        conn.close()

# Create logs folder if it doesn't exist
import os
os.makedirs('logs', exist_ok=True)

# Start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 2222))
server.listen(100)

print('[*] SSH Honeypot running on port 2222...')
print('[*] Sending attacks to Kafka topic: honeypot-attacks')

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()