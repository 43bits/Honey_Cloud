# scripts/test_kafka_flow.py
"""
Tests the complete Kafka → API store flow in isolation.
"""
import sys, os, json, time, threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 50)
print("  Kafka Flow Test")
print("=" * 50)

# ── Step 1: Check Kafka is running ─────────────────
print("\n[1] Checking Kafka...")
try:
    from kafka import KafkaProducer, KafkaConsumer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )
    print("   ✓ Kafka producer connected")
except Exception as e:
    print(f"   ✗ Kafka ERROR: {e}")
    print("   Run: docker-compose up -d")
    sys.exit(1)

# ── Step 2: Send a test message ────────────────────
print("\n[2] Sending test attack to Kafka...")
test_log = {
    'source_ip':     '185.234.219.4',
    'source_port':   54321,
    'port_targeted': 22,
    'protocol':      'tcp',
    'country':       'Russia',
    'timestamp':     time.strftime('%Y-%m-%d %H:%M:%S'),
}
producer.send('honeypot-attacks', test_log)
producer.flush()
producer.close()
print(f"   ✓ Sent: {test_log['source_ip']} → port {test_log['port_targeted']}")

# ── Step 3: Check if API received it ──────────────
print("\n[3] Waiting 5 seconds for API to process...")
time.sleep(5)

try:
    import urllib.request
    url = 'http://localhost:8000/attacks?limit=5'
    with urllib.request.urlopen(url, timeout=5) as r:
        data = json.loads(r.read())
    attacks = data.get('attacks', [])
    print(f"   API has {data.get('count', 0)} attacks stored")
    if attacks:
        latest = attacks[0]
        print(f"   Latest: {latest.get('source_ip')} "
              f"→ {latest.get('attack_type')} "
              f"[{latest.get('risk_level')}]")
        print("   ✓ Kafka → API flow WORKING")
    else:
        print("   ✗ API store is empty — Kafka consumer not feeding store")
except Exception as e:
    print(f"   ✗ API check failed: {e}")
    print("   Is the API running? uvicorn api.threat_api:app --reload")

# ── Step 4: Check consumer group offset ───────────
print("\n[4] Checking Kafka consumer group...")
try:
    consumer = KafkaConsumer(
        bootstrap_servers=['localhost:9092'],
        group_id='test-diagnostic-group',
        auto_offset_reset='latest',
        consumer_timeout_ms=3000,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    )
    consumer.subscribe(['honeypot-attacks'])
    consumer.poll(timeout_ms=1000)
    partitions = consumer.partitions_for_topic('honeypot-attacks')
    print(f"   ✓ Topic 'honeypot-attacks' has partitions: {partitions}")
    consumer.close()
except Exception as e:
    print(f"   ✗ Consumer check failed: {e}")

print("\n" + "=" * 50)
print("  Flow test complete")
print("=" * 50)