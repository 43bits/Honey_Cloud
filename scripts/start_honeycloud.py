# scripts/start_honeycloud.py
import subprocess
import sys
import time
import os

print("""
╔══════════════════════════════════════╗
║     HoneyCloud Sentinel v1.0         ║
║     Starting all services...         ║
╚══════════════════════════════════════╝
""")

# 1. Start Kafka
print("[1/3] Starting Kafka...")
subprocess.Popen(["docker-compose", "up", "-d"])
time.sleep(10)  # wait for Kafka to be ready
print("      Kafka ready ✓")

# 2. Start Kafka consumer (ML pipeline) in background
print("[2/3] Starting ML Consumer...")
consumer_proc = subprocess.Popen(
    [sys.executable, "data_pipeline/kafka_consumer.py"],
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
time.sleep(2)
print("      ML Consumer ready ✓")

# 3. Start FastAPI
print("[3/3] Starting API server...")
print("      API running at http://localhost:8000")
print("      Docs at        http://localhost:8000/docs\n")
os.system("uvicorn api.threat_api:app --reload --host 0.0.0.0 --port 8000")