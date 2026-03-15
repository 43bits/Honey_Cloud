# data_pipeline/kafka_producer.py
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_attack_log(log_data):
    """Send a single attack log to Kafka."""
    future = producer.send('honeypot-attacks', log_data)
    producer.flush()
    print(f"[+] Sent to Kafka: {log_data.get('attack_type', 'unknown')} from {log_data.get('source_ip', '?')}")
    return future