# data_pipeline/kafka_consumer.py
from kafka import KafkaConsumer
import json

def start_consumer():
    consumer = KafkaConsumer(
        'honeypot-attacks',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',       # start from beginning
        enable_auto_commit=True,
        group_id='honeypot-ml-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print('[*] Kafka Consumer started. Waiting for attacks...')
    print('[*] Press Ctrl+C to stop\n')

    for message in consumer:
        log = message.value

        print(f"--- New Attack Received ---")
        print(f"  IP:        {log.get('source_ip', 'unknown')}")
        print(f"  Protocol:  {log.get('protocol', 'unknown')}")
        print(f"  Port:      {log.get('port_targeted', 'unknown')}")
        print(f"  Time:      {log.get('timestamp', 'unknown')}")
        print(f"  Data:      {log.get('data_hex', '')[:20]}...")
        print()

        # TODO: Phase 4 will add ML prediction here

if __name__ == '__main__':
    start_consumer()