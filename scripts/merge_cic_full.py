# scripts/merge_cic_full.py
"""
Merges full CIC extraction into final unified dataset
and retrains all models.
"""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

UNIFIED_WITH_TEST = 'datasets/unified_training_with_cic.csv'
CIC_FULL_PATH     = 'datasets/cic_full_extracted.csv'
FINAL_OUTPUT      = 'datasets/unified_final.csv'

TRAIN_COLS = [
    'src_port', 'dst_port', 'protocol',
    'dataset_source', 'is_dangerous_port',
    'port_category', 'is_high_port',
    'attack_label', 'dataset_source_name',
]


def merge():
    print("[*] Loading existing dataset...")
    existing = pd.read_csv(UNIFIED_WITH_TEST)
    print(f"    Rows: {len(existing):,}")

    print("[*] Loading full CIC extraction...")
    cic = pd.read_csv(CIC_FULL_PATH)
    print(f"    Rows: {len(cic):,}")

    # Align columns
    common = [c for c in TRAIN_COLS
              if c in existing.columns and c in cic.columns]

    combined = pd.concat(
        [existing[common], cic[common]],
        ignore_index=True
    )
    combined = combined.sample(frac=1, random_state=42)\
                       .reset_index(drop=True)
    combined.to_csv(FINAL_OUTPUT, index=False)

    print(f"\n{'='*55}")
    print(f"  FINAL UNIFIED DATASET")
    print(f"{'='*55}")
    print(f"  Total rows: {len(combined):,}")
    print(f"\n  By source:")
    if 'dataset_source_name' in combined.columns:
        print(combined['dataset_source_name']
              .value_counts().to_string())
    print(f"\n  By attack label:")
    print(combined['attack_label'].value_counts().to_string())
    print(f"\n[✓] Saved to: {FINAL_OUTPUT}")


if __name__ == '__main__':
    merge()