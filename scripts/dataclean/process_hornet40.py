# scripts/process_hornet40.py
"""
Processes Hornet 40 hourly traffic data and summary table.
Creates:
  1. datasets/hornet40_processed.csv  — hourly stats
  2. datasets/hornet41_geo.csv        — geo metadata
"""
import pandas as pd
import numpy as np

# ── Hornet 40 — hourly traffic per honeypot ────────
H40_INPUT  = r'F:\CyberSecurity\honeycloud\datasets\tcfzkbpw46-3\hornet40-traffic-per-honeypot-hourly-comparative.csv'
H41_INPUT  = r'F:\CyberSecurity\honeycloud\datasets\tcfzkbpw46-3\Hornet40-Dataset-Summary-Table.csv'
H40_OUTPUT = r'F:\CyberSecurity\honeycloud\datasets\hornet40_processed.csv'
H41_OUTPUT = r'F:\CyberSecurity\honeycloud\datasets\hornet41_geo.csv'

print("[*] Processing Hornet 40 hourly traffic...")
h40 = pd.read_csv(H40_INPUT, on_bad_lines='skip')

# Rename honeypot columns to city names (from Hornet 41 summary)
honeypot_city_map = {
    'Honeypot-Cloud-DigitalOcean-Geo-1': 'Amsterdam',
    'Honeypot-Cloud-DigitalOcean-Geo-2': 'Bangalore',
    'Honeypot-Cloud-DigitalOcean-Geo-3': 'Frankfurt',
    'Honeypot-Cloud-DigitalOcean-Geo-4': 'London',
    'Honeypot-Cloud-DigitalOcean-Geo-5': 'New York',
    'Honeypot-Cloud-DigitalOcean-Geo-6': 'San Francisco',
    'Honeypot-Cloud-DigitalOcean-Geo-7': 'Singapore',
    'Honeypot-Cloud-DigitalOcean-Geo-8': 'Toronto',
}

h40 = h40.rename(columns=honeypot_city_map)
h40['_time'] = pd.to_datetime(h40['_time'], utc=True, errors='coerce')

# Melt to long format: one row per (timestamp, city, count)
city_cols = list(honeypot_city_map.values())
h40_long  = h40.melt(
    id_vars=['_time'],
    value_vars=city_cols,
    var_name='city',
    value_name='attack_count',
)

h40_long['hour']    = h40_long['_time'].dt.hour
h40_long['weekday'] = h40_long['_time'].dt.day_name()

h40_long.to_csv(H40_OUTPUT, index=False)
print(f"[✓] Hornet 40 processed: {len(h40_long)} rows → {H40_OUTPUT}")

# ── Hornet 41 — geo summary ───────────────────────
print("\n[*] Processing Hornet 41 summary table...")
h41 = pd.read_csv(H41_INPUT, on_bad_lines='skip')

# Clean numeric columns
for col in ['Total Unique Src IPs', 'Total Flows',
            'Total Bytes', 'Total Packets',
            'TCP Flows', 'UDP Flows', 'ICMP Flows']:
    if col in h41.columns:
        h41[col] = h41[col].astype(str).str.replace(',','').str.strip()
        h41[col] = pd.to_numeric(h41[col], errors='coerce').fillna(0).astype(int)

# Map honeypot name to city
h41['city'] = h41['Honeypot'].map(honeypot_city_map)

h41.to_csv(H41_OUTPUT, index=False)
print(f"[✓] Hornet 41 processed: {len(h41)} rows → {H41_OUTPUT}")

# Print summary
print("\n[*] Hornet 40 stats per city:")
city_stats = h40_long.groupby('city')['attack_count'].agg(['sum','mean','max'])
print(city_stats.sort_values('sum', ascending=False).to_string())

print("\n[*] Hornet 41 geo summary:")
print(h41[['city','Region','Total Unique Src IPs','Total Flows']].to_string())