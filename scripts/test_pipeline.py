# scripts/test_pipeline.py
import json
import time
import datetime
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

attack_types = ['SSH Brute Force', 'Port Scan', 'Malware Upload', 'SQL Injection', 'Botnet']
ips = ['185.234.219.4', '45.91.200.12', '192.168.1.100', '103.27.186.5', '91.240.118.33']

print('[*] Sending 10 test attacks to Kafka...')

for i in range(10):
    fake_log = {
        'timestamp': str(datetime.datetime.now()),
        'source_ip': random.choice(ips),
        'source_port': random.randint(1024, 65535),
        'port_targeted': random.choice([22, 80, 21, 3306]),
        'protocol': random.choice(['SSH', 'HTTP', 'FTP']),
        'attack_type': random.choice(attack_types),
        'login_attempts': random.randint(1, 500),
        'connection_rate': round(random.uniform(0.1, 50.0), 2),
        'data_hex': 'deadbeef1234'
    }

    producer.send('honeypot-attacks', fake_log)
    print(f"  [{i+1}] Sent: {fake_log['attack_type']} from {fake_log['source_ip']}")
    time.sleep(0.5)

producer.flush()
print('\n[+] Done! Run the consumer to see them.')