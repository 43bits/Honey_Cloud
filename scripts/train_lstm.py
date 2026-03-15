# scripts/train_lstm.py
"""
Train the LSTM attack predictor.
Run this after you have collected some attack data,
or use the demo data below.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_models.PredictionEngine.attack_predictor import train_lstm

# Use real attacks from your store if available
try:
    import requests
    res     = requests.get('http://localhost:8000/attacks?limit=200')
    attacks = res.json().get('attacks', [])
    types   = [a.get('attack_type', 'Port Scan / Other') for a in attacks]
    print(f"[*] Using {len(types)} real attacks from API")
except Exception:
    types = []

# Fall back to synthetic training data if not enough real data
if len(types) < 20:
    print("[*] Using synthetic training sequences...")
    # Realistic attack patterns
    types = (
        ['Port Scan / Other', 'SSH Brute Force',
         'SSH Brute Force', 'SSH Brute Force'] * 15
        + ['Web Exploit', 'Web Exploit',
           'Database Attack', 'Database Attack'] * 10
        + ['Port Scan / Other', 'FTP Attack',
           'FTP Attack', 'SSH Brute Force'] * 8
        + ['Telnet Attack', 'Telnet Attack',
           'Database Attack'] * 6
        + ['SSH Brute Force', 'Web Exploit',
           'Database Attack', 'Port Scan / Other'] * 12
    )

print(f"[*] Training on {len(types)} attack events...")
train_lstm(types)
print("\n[✓] LSTM training complete!")
print("[✓] Model saved to models/lstm_predictor.keras")