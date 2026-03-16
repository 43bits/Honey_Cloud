# scripts/merge_with_cic.py
"""
Merges CIC test extraction into unified_training.csv
and retrains all models.
"""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

UNIFIED_PATH = 'datasets/unified_training.csv'
CIC_PATH     = 'datasets/cic_test_extracted.csv'
OUTPUT_PATH  = 'datasets/unified_training_with_cic.csv'


def merge():
    print("[*] Loading existing unified dataset...")
    existing = pd.read_csv(UNIFIED_PATH)
    print(f"    Existing rows: {len(existing):,}")
    print(f"    Sources: {existing['dataset_source'].value_counts().to_dict()}")

    print("\n[*] Loading CIC extracted data...")
    cic = pd.read_csv(CIC_PATH)
    print(f"    CIC rows: {len(cic):,}")

    # Align columns — keep only standard training columns
    TRAIN_COLS = [
        'src_port', 'dst_port', 'protocol',
        'dataset_source', 'is_dangerous_port',
        'port_category', 'is_high_port',
        'attack_label', 'dataset_source_name',
    ]

    # Add missing columns to existing
    if 'dataset_source_name' not in existing.columns:
        existing['dataset_source_name'] = existing['dataset_source']\
            .map({0: 'aws', 1: 'dionaea', 2: 'cic'}).fillna('aws')

    # Only keep columns that exist in both
    cic_cols      = [c for c in TRAIN_COLS if c in cic.columns]
    existing_cols = [c for c in TRAIN_COLS if c in existing.columns]
    common_cols   = list(set(cic_cols) & set(existing_cols))

    combined = pd.concat(
        [existing[common_cols], cic[common_cols]],
        ignore_index=True
    )
    
    # In scripts/merge_with_cic.py — add this after concat:
    combined['dataset_source_name'] = combined['dataset_source'].map({0: 'aws', 1: 'dionaea', 2: 'cic'}).fillna('aws')

    # Shuffle
    combined = combined.sample(frac=1, random_state=42)\
        .reset_index(drop=True)

    combined.to_csv(OUTPUT_PATH, index=False)

    print(f"\n{'='*55}")
    print(f"  MERGED DATASET SUMMARY")
    print(f"{'='*55}")
    print(f"  Total rows: {len(combined):,}")
    print(f"\n  By source:")
    print(combined['dataset_source_name'].value_counts().to_string())
    print(f"\n  By attack label:")
    print(combined['attack_label'].value_counts().to_string())
    print(f"\n[✓] Saved to: {OUTPUT_PATH}")


if __name__ == '__main__':
    merge()