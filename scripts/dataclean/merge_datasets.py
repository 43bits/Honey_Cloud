# scripts/merge_datasets.py
"""
Merges AWS + Dionaea into one unified training dataset.
Hornet 40 is used separately for geo stats (different format).
"""
import pandas as pd
import numpy as np
import os

AWS_PATH     = r'F:\CyberSecurity\honeycloud\datasets\AWS_Honeypot_marx-geo.csv'
DIONAEA_PATH = r'F:\CyberSecurity\honeycloud\datasets\dionaea_fixed.csv'
OUTPUT_PATH  = r'F:\CyberSecurity\honeycloud\datasets\unified_training.csv'


def normalize_aws(path: str) -> pd.DataFrame:
    print("[*] Loading AWS Honeypot dataset...")
    df = pd.read_csv(path, on_bad_lines='skip', low_memory=False)

    out = pd.DataFrame()
    out['src_port']       = pd.to_numeric(df['spt'], errors='coerce').fillna(0).astype(int)
    out['dst_port']       = pd.to_numeric(df['dpt'], errors='coerce').fillna(0).astype(int)
    out['protocol']       = df['proto'].str.upper().fillna('TCP')
    out['country']        = df['country'].fillna('Unknown')
    out['dataset_source'] = 'aws'

    # Label from port
    out['attack_label'] = out['dst_port'].apply(label_from_port)

    out = out.dropna(subset=['dst_port'])
    out = out[out['dst_port'] > 0]

    print(f"[✓] AWS: {len(out)} rows after cleaning")
    return out


def normalize_dionaea(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"[!] Dionaea fixed file not found: {path}")
        print("[!] Run scripts/fix_dionaea.py first")
        return pd.DataFrame()

    print("[*] Loading Dionaea dataset...")
    df = pd.read_csv(path, on_bad_lines='skip', low_memory=False)

    out = pd.DataFrame()
    out['src_port']       = pd.to_numeric(df.get('src_port', 0), errors='coerce').fillna(0).astype(int)
    out['dst_port']       = pd.to_numeric(df.get('dst_port', 0), errors='coerce').fillna(0).astype(int)
    out['protocol']       = df.get('proto', 'TCP').fillna('TCP')
    out['country']        = 'Unknown'
    out['dataset_source'] = 'dionaea'

    out['attack_label'] = out['dst_port'].apply(label_from_port)

    out = out.dropna(subset=['dst_port'])
    out = out[out['dst_port'] > 0]

    print(f"[✓] Dionaea: {len(out)} rows after cleaning")
    return out


def label_from_port(port: int) -> str:
    """
    Label attack type from destination port.
    Same logic used in attack_classifier.py.
    """
    port = int(port)
    if port == 22:                          return 'SSH Brute Force'
    elif port in [80, 8080, 443, 8443]:     return 'Web Exploit'
    elif port in [3306, 5432, 1433, 27017,
                  6379, 5984, 9200]:        return 'Database Attack'
    elif port == 21:                        return 'FTP Attack'
    elif port == 23:                        return 'Telnet Attack'
    elif port in [445, 135, 139]:           return 'SMB Attack'
    elif port in [25, 587, 465]:            return 'Email Attack'
    elif port in [53]:                      return 'DNS Attack'
    else:                                   return 'Port Scan / Other'


def merge_and_save():
    aws     = normalize_aws(AWS_PATH)
    dionaea = normalize_dionaea(DIONAEA_PATH)

    frames = [df for df in [aws, dionaea] if len(df) > 0]

    if not frames:
        print("[!] No datasets loaded")
        return

    unified = pd.concat(frames, ignore_index=True)

    # Final cleanup
    unified = unified.dropna(subset=['dst_port', 'attack_label'])
    unified = unified[unified['dst_port'] > 0]
    unified = unified[unified['dst_port'] < 65536]

    # Shuffle for better training
    unified = unified.sample(frac=1, random_state=42).reset_index(drop=True)

    unified.to_csv(OUTPUT_PATH, index=False)

    print(f"\n{'='*55}")
    print(f"  UNIFIED DATASET SUMMARY")
    print(f"{'='*55}")
    print(f"  Total rows:    {len(unified):,}")
    print(f"\n  By source:")
    print(unified['dataset_source'].value_counts().to_string())
    print(f"\n  By attack label:")
    print(unified['attack_label'].value_counts().to_string())
    print(f"\n  By protocol:")
    print(unified['protocol'].value_counts().to_string())
    print(f"\n[✓] Saved to: {OUTPUT_PATH}")

    return unified


if __name__ == '__main__':
    merge_and_save()