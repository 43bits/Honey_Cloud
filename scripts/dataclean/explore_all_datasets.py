# scripts/explore_all_datasets.py
import pandas as pd
import os

datasets = {
    'AWS Honeypot':  r'F:\CyberSecurity\honeycloud\datasets\AWS_Honeypot_marx-geo.csv',
    'Dionaea':       r'F:\CyberSecurity\honeycloud\datasets\dionaeaClean2.csv',
    'Hornet 40':     r'F:\CyberSecurity\honeycloud\datasets\tcfzkbpw46-3\hornet40-traffic-per-honeypot-hourly-comparative.csv',
    'Hornet 41':     r'F:\CyberSecurity\honeycloud\datasets\tcfzkbpw46-3\Hornet40-Dataset-Summary-Table.csv',
}

for name, path in datasets.items():
    if not os.path.exists(path):
        print(f"\n[MISSING] {name} — {path}")
        continue

    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    try:
        # Try different encodings and skip bad lines
        for enc in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(
                    path,
                    nrows=5000,
                    encoding=enc,
                    on_bad_lines='skip',   # skip malformed rows
                    sep=None,              # auto-detect separator
                    engine='python',
                )
                print(f"  Encoding: {enc}")
                break
            except Exception:
                continue

        print(f"  Rows (sample): {len(df)}")
        print(f"  Columns ({len(df.columns)}): {df.columns.tolist()}")
        print(f"\n  Dtypes:")
        print(df.dtypes.to_string())
        print(f"\n  First row:")
        for k, v in df.iloc[0].to_dict().items():
            print(f"    {k}: {v}")
        print(f"\n  Null counts:")
        nulls = df.isnull().sum()
        print(nulls[nulls > 0].to_string() if nulls.sum() > 0 else "    None")
        print(f"\n  Unique values in key columns:")
        for col in df.columns[:8]:
            uq = df[col].nunique()
            print(f"    {col}: {uq} unique")

    except Exception as e:
        print(f"  ERROR: {e}")