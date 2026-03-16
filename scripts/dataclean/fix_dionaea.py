# scripts/fix_dionaea.py
"""
Fixes the Dionaea CSV which has scrambled column headers.
Run this ONCE to generate a clean version.
"""
import pandas as pd
import os

INPUT  = r'F:\CyberSecurity\honeycloud\datasets\dionaeaClean2.csv'
OUTPUT = r'F:\CyberSecurity\honeycloud\datasets\dionaea_fixed.csv'

print("[*] Loading Dionaea dataset with bad line skipping...")
df = pd.read_csv(
    INPUT,
    on_bad_lines='skip',
    engine='python',
    encoding='utf-8',
)

print(f"[*] Raw shape: {df.shape}")
print(f"[*] Raw columns: {df.columns.tolist()}")

# Rename scrambled columns to their actual meaning
df.columns = [c.strip() for c in df.columns]  # strip spaces

# Based on exploration output — actual data meaning:
# 'protocol'   → protocol (tcp)
# 'transport'  → connection type
# 'type'       → dst_port (the targeted port number)
# 'dst_port'   → src_ip (attacker IP as string)
# 'src_ip'     → src_port
# 'src_port'   → timestamp string
# 'timestamp'  → NaN (drop)

df = df.rename(columns={
    'protocol':  'protocol',
    'transport': 'transport',
    'type':      'dst_port',
    'dst_port':  'src_ip_str',
    'src_ip':    'src_port',
    'src_port':  'timestamp',
    'timestamp': 'drop_col',
})

# Drop the empty column
if 'drop_col' in df.columns:
    df = df.drop(columns=['drop_col'])

# Clean dst_port — keep only numeric rows
df['dst_port'] = pd.to_numeric(df['dst_port'], errors='coerce')
df = df.dropna(subset=['dst_port'])
df['dst_port'] = df['dst_port'].astype(int)

# Clean src_port
df['src_port'] = pd.to_numeric(df['src_port'], errors='coerce').fillna(0).astype(int)

# Add dataset source tag
df['dataset_source'] = 'dionaea'
df['country']        = 'Unknown'  # Dionaea doesn't have geo
df['proto']          = df['protocol'].str.upper().fillna('TCP')

print(f"\n[*] Fixed shape: {df.shape}")
print(f"[*] Fixed columns: {df.columns.tolist()}")
print(f"\n[*] Sample cleaned row:")
print(df.iloc[0].to_dict())
print(f"\n[*] Unique dst_ports: {df['dst_port'].unique()[:20]}")
print(f"[*] Port distribution:")
print(df['dst_port'].value_counts().head(10))

df.to_csv(OUTPUT, index=False)
print(f"\n[✓] Saved cleaned Dionaea to: {OUTPUT}")