# scripts/extract_pcap_test.py
"""
Phase 2.1 — Extract features from 3 test .pcap files.
Tests the pipeline before running on full 7GB dataset.
"""
import subprocess
import pandas as pd
import os
import sys
import time

# ── Config ─────────────────────────────────────────────
TSHARK_PATH = r'D:\SOLFWARE INSTALL\wireShark\tshark.exe'

TEST_FILES = [
    r'F:\CyberSecurity\honeycloud\datasets\CICHoneynet2023\CICHoneynet_7-2July..pcap',
    r'F:\CyberSecurity\honeycloud\datasets\CICHoneynet2023\CICHoneynet_7July..pcap',
    r'F:\CyberSecurity\honeycloud\datasets\CICHoneynet2023\CICHoneynet_4 July.pcap',
]

OUTPUT_CSV  = r'F:\CyberSecurity\honeycloud\datasets\cic_test_extracted.csv'

# ── Fields to extract ──────────────────────────────────
# tshark field name → our column name
FIELDS = {
    'ip.src':            'src_ip',
    'ip.dst':            'dst_ip',
    'tcp.srcport':       'src_port',
    'tcp.dstport':       'dst_port_tcp',
    'udp.srcport':       'udp_src_port',
    'udp.dstport':       'udp_dst_port',
    'ip.proto':          'protocol_num',
    'frame.len':         'frame_len',
    'ip.ttl':            'ttl',
    'tcp.flags':         'tcp_flags',
    'tcp.window_size':   'tcp_window',
    'frame.time_epoch':  'timestamp',
    'ip.len':            'ip_len',
}

TSHARK_FIELDS = list(FIELDS.keys())
OUR_COLUMNS   = list(FIELDS.values())


def extract_pcap(pcap_path: str) -> pd.DataFrame:
    """Extract features from a single .pcap file using tshark."""

    filename = os.path.basename(pcap_path)
    print(f"\n[*] Processing: {filename}")
    print(f"    Size: {os.path.getsize(pcap_path) / 1024 / 1024:.1f} MB")

    # Build tshark command
    # -r = read file
    # -T fields = output as tab-separated fields
    # -e = field to extract
    # -E header=y = include header row
    # -E separator=, = use comma separator
    # -E quote=d = double-quote strings
    # -E occurrence=f = first occurrence only

    cmd = [
        TSHARK_PATH,
        '-r', pcap_path,
        '-T', 'fields',
        '-E', 'header=y',
        '-E', 'separator=,',
        '-E', 'quote=d',
        '-E', 'occurrence=f',
    ]

    # Add each field
    for field in TSHARK_FIELDS:
        cmd.extend(['-e', field])

    print(f"    Running tshark...")
    start = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,   # 5 minute timeout per file
        )

        if result.returncode != 0:
            print(f"    ✗ tshark error: {result.stderr[:200]}")
            return pd.DataFrame()

        elapsed = round(time.time() - start, 1)
        print(f"    tshark finished in {elapsed}s")

        # Parse output into DataFrame
        from io import StringIO
        df = pd.read_csv(
            StringIO(result.stdout),
            low_memory=False,
            on_bad_lines='skip',
        )

        print(f"    Raw rows extracted: {len(df):,}")
        return df

    except subprocess.TimeoutExpired:
        print(f"    ✗ Timeout after 5 minutes")
        return pd.DataFrame()
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return pd.DataFrame()


def normalize_cic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize raw tshark output into our standard 7-feature format.
    """
    if df.empty:
        return pd.DataFrame()

    # Rename columns to our names
    df.columns = OUR_COLUMNS[:len(df.columns)]

    out = pd.DataFrame()

    # Source port — prefer TCP, fall back to UDP
    tcp_src = pd.to_numeric(df.get('src_port', 0),     errors='coerce').fillna(0)
    udp_src = pd.to_numeric(df.get('udp_src_port', 0), errors='coerce').fillna(0)
    out['src_port'] = tcp_src.where(tcp_src > 0, udp_src).astype(int)

    # Destination port — prefer TCP, fall back to UDP
    tcp_dst = pd.to_numeric(df.get('dst_port_tcp', 0), errors='coerce').fillna(0)
    udp_dst = pd.to_numeric(df.get('udp_dst_port', 0), errors='coerce').fillna(0)
    out['dst_port'] = tcp_dst.where(tcp_dst > 0, udp_dst).astype(int)

    # Protocol: 6=TCP→0, 17=UDP→1, 1=ICMP→2, other→3
    proto_num = pd.to_numeric(
        df.get('protocol_num', 6), errors='coerce'
    ).fillna(6).astype(int)
    proto_map = {6: 0, 17: 1, 1: 2}
    out['protocol'] = proto_num.map(proto_map).fillna(3).astype(int)

    # Dataset source
    out['dataset_source'] = 2   # 2 = CIC Honeynet

    # Dangerous port flag
    from ml_models.feature_engineering import DANGEROUS_PORTS, categorize_port
    out['is_dangerous_port'] = out['dst_port']\
        .isin(DANGEROUS_PORTS).astype(int)

    # Port category
    out['port_category'] = out['dst_port']\
        .apply(categorize_port).astype(int)

    # Is high source port (scanner behaviour)
    out['is_high_port'] = (out['src_port'] > 1024).astype(int)

    # Attack label from destination port
    from scripts.dataclean.merge_datasets import label_from_port
    out['attack_label'] = out['dst_port'].apply(label_from_port)

    # Extra CIC-specific features for enrichment
    out['frame_len']   = pd.to_numeric(
        df.get('frame_len', 0), errors='coerce'
    ).fillna(0).astype(int)
    out['ttl']         = pd.to_numeric(
        df.get('ttl', 0), errors='coerce'
    ).fillna(0).astype(int)
    out['ip_len']      = pd.to_numeric(
        df.get('ip_len', 0), errors='coerce'
    ).fillna(0).astype(int)

    # Dataset source tag
    out['dataset_source_name'] = 'cic'

    # Drop rows with no destination port
    out = out[out['dst_port'] > 0]
    out = out[out['dst_port'] < 65536]

    return out


def run_test_extraction():
    print("=" * 55)
    print("  CIC Honeynet — Phase 2.1 Test Extraction")
    print("=" * 55)

    # Check tshark exists
    if not os.path.exists(TSHARK_PATH):
        print(f"\n[!] tshark not found at: {TSHARK_PATH}")
        print("[!] Try: where tshark")
        sys.exit(1)

    print(f"\n[✓] tshark found: {TSHARK_PATH}")

    all_frames = []

    for pcap_path in TEST_FILES:
        if not os.path.exists(pcap_path):
            print(f"\n[!] File not found: {pcap_path}")
            continue

        raw_df  = extract_pcap(pcap_path)
        if raw_df.empty:
            print(f"    [!] No data extracted")
            continue

        norm_df = normalize_cic(raw_df)
        print(f"    After normalization: {len(norm_df):,} rows")
        print(f"    Attack label distribution:")
        print(norm_df['attack_label'].value_counts().to_string())

        all_frames.append(norm_df)

    if not all_frames:
        print("\n[!] No data extracted from any file")
        return

    # Combine all test extractions
    combined = pd.concat(all_frames, ignore_index=True)

    print(f"\n{'='*55}")
    print(f"  TEST EXTRACTION SUMMARY")
    print(f"{'='*55}")
    print(f"  Total rows:    {len(combined):,}")
    print(f"  Attack labels:")
    print(combined['attack_label'].value_counts().to_string())
    print(f"\n  Sample row:")
    print(combined.iloc[0].to_dict())

    # Save test output
    combined.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[✓] Saved to: {OUTPUT_CSV}")
    print(f"\n  Next step: run scripts/merge_with_cic.py")


if __name__ == '__main__':
    run_test_extraction()