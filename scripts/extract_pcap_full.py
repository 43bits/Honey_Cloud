# scripts/extract_pcap_full.py
"""
Phase 2.2 — Process all CIC Honeynet .pcap files.
Handles normal files in batch and giant files in chunks.
"""
import subprocess
import pandas as pd
import os
import sys
import time
import glob
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Config ─────────────────────────────────────────
TSHARK_PATH  = r'D:\SOLFWARE INSTALL\wireShark\tshark.exe'
PCAP_FOLDER  = r'F:\CyberSecurity\honeycloud\datasets\CICHoneynet2023'
OUTPUT_FOLDER = r'F:\CyberSecurity\honeycloud\datasets\cic_extracted'
FINAL_CSV    = r'F:\CyberSecurity\honeycloud\datasets\cic_full_extracted.csv'

# Files to skip — corrupted or already processed in test
SKIP_FILES = {
    'CICHoneynet_6July..pcap',     # 0MB corrupted
    'CICHoneynet_7-2July..pcap',   # 6.4MB corrupted
    'CICHoneynet_7July..pcap',     # already in test
    'CICHoneynet_4 July.pcap',     # already in test
}

# Giant files — process separately with chunking
GIANT_FILES = {
    'CICHoneynet_24July..pcap',    # 5GB
    'CICHoneynet_31July..pcap',    # 7GB
}

# tshark fields
TSHARK_FIELDS = [
    'ip.src', 'ip.dst',
    'tcp.srcport', 'tcp.dstport',
    'udp.srcport', 'udp.dstport',
    'ip.proto', 'frame.len',
    'ip.ttl', 'tcp.flags',
    'tcp.window_size', 'frame.time_epoch',
    'ip.len',
]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ── Helpers ─────────────────────────────────────────

def build_tshark_cmd(pcap_path: str) -> list:
    cmd = [
        TSHARK_PATH,
        '-r', pcap_path,
        '-T', 'fields',
        '-E', 'header=y',
        '-E', 'separator=,',
        '-E', 'quote=d',
        '-E', 'occurrence=f',
    ]
    for field in TSHARK_FIELDS:
        cmd.extend(['-e', field])
    return cmd


def normalize_raw(df: pd.DataFrame) -> pd.DataFrame:
    """Convert raw tshark output to standard 7-feature format."""
    from ml_models.feature_engineering import DANGEROUS_PORTS, categorize_port
    from scripts.dataclean.merge_datasets import label_from_port

    if df.empty:
        return pd.DataFrame()

    # Rename columns
    col_map = {
        'ip.src':           'src_ip',
        'ip.dst':           'dst_ip',
        'tcp.srcport':      'src_port',
        'tcp.dstport':      'dst_port_tcp',
        'udp.srcport':      'udp_src_port',
        'udp.dstport':      'udp_dst_port',
        'ip.proto':         'protocol_num',
        'frame.len':        'frame_len',
        'ip.ttl':           'ttl',
        'tcp.flags':        'tcp_flags',
        'tcp.window_size':  'tcp_window',
        'frame.time_epoch': 'timestamp',
        'ip.len':           'ip_len',
    }
    df = df.rename(columns=col_map)

    out = pd.DataFrame()

    tcp_src = pd.to_numeric(df.get('src_port', 0),     errors='coerce').fillna(0)
    udp_src = pd.to_numeric(df.get('udp_src_port', 0), errors='coerce').fillna(0)
    out['src_port'] = tcp_src.where(tcp_src > 0, udp_src).astype(int)

    tcp_dst = pd.to_numeric(df.get('dst_port_tcp', 0), errors='coerce').fillna(0)
    udp_dst = pd.to_numeric(df.get('udp_dst_port', 0), errors='coerce').fillna(0)
    out['dst_port'] = tcp_dst.where(tcp_dst > 0, udp_dst).astype(int)

    proto_num = pd.to_numeric(
        df.get('protocol_num', 6), errors='coerce'
    ).fillna(6).astype(int)
    out['protocol']          = proto_num.map({6:0, 17:1, 1:2}).fillna(3).astype(int)
    out['dataset_source']    = 2
    out['is_dangerous_port'] = out['dst_port'].isin(DANGEROUS_PORTS).astype(int)
    out['port_category']     = out['dst_port'].apply(categorize_port).astype(int)
    out['is_high_port']      = (out['src_port'] > 1024).astype(int)
    out['attack_label']      = out['dst_port'].apply(label_from_port)
    out['dataset_source_name'] = 'cic'

    out = out[out['dst_port'] > 0]
    out = out[out['dst_port'] < 65536]
    return out


def save_checkpoint(df: pd.DataFrame, filename: str):
    """Save per-file checkpoint so progress isn't lost if crash."""
    path = os.path.join(OUTPUT_FOLDER, filename)
    df.to_csv(path, index=False)
    return path


def already_processed(filename: str) -> bool:
    """Check if checkpoint exists for this file."""
    checkpoint = os.path.join(OUTPUT_FOLDER, filename)
    return os.path.exists(checkpoint)


# ── Normal file processor ───────────────────────────

def process_normal_file(pcap_path: str) -> pd.DataFrame:
    """Process a single normal-sized .pcap file."""
    filename = os.path.basename(pcap_path)
    checkpoint_name = filename.replace('.pcap', '.csv')\
                               .replace('..', '_')

    # Skip if already processed
    if already_processed(checkpoint_name):
        print(f"  [SKIP] Already processed: {filename}")
        return pd.read_csv(
            os.path.join(OUTPUT_FOLDER, checkpoint_name)
        )

    size_mb = os.path.getsize(pcap_path) / 1024 / 1024
    print(f"\n  Processing: {filename} ({size_mb:.1f} MB)")

    cmd    = build_tshark_cmd(pcap_path)
    start  = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            stderr = result.stderr[:300]
            if 'cut short' in stderr or 'appear' in stderr:
                print(f"  [SKIP] Corrupted file: {filename}")
            else:
                print(f"  [ERROR] {stderr}")
            return pd.DataFrame()

        elapsed = round(time.time() - start, 1)
        raw     = pd.read_csv(
            StringIO(result.stdout),
            low_memory=False,
            on_bad_lines='skip',
        )

        norm = normalize_raw(raw)
        if not norm.empty:
            save_checkpoint(norm, checkpoint_name)
            print(f"  ✓ {len(norm):,} rows in {elapsed}s "
                  f"→ {checkpoint_name}")

        return norm

    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {filename} — skipping")
        return pd.DataFrame()
    except Exception as e:
        print(f"  [ERROR] {filename}: {e}")
        return pd.DataFrame()


# ── Giant file processor (chunked) ──────────────────

def process_giant_file(pcap_path: str,
                       chunk_packets: int = 500_000) -> pd.DataFrame:
    """
    Process giant .pcap files in chunks of N packets.
    Prevents RAM overflow on Windows.
    """
    filename    = os.path.basename(pcap_path)
    size_mb     = os.path.getsize(pcap_path) / 1024 / 1024
    base_name   = filename.replace('.pcap', '').replace('..', '_')

    print(f"\n  GIANT FILE: {filename} ({size_mb:.0f} MB)")
    print(f"  Processing in chunks of {chunk_packets:,} packets...")

    all_chunks  = []
    chunk_num   = 0
    offset      = 0
    total_rows  = 0

    while True:
        chunk_name = f"{base_name}_chunk{chunk_num:04d}.csv"

        if already_processed(chunk_name):
            print(f"  [SKIP] Chunk {chunk_num} already done")
            chunk_df = pd.read_csv(
                os.path.join(OUTPUT_FOLDER, chunk_name)
            )
            all_chunks.append(chunk_df)
            total_rows += len(chunk_df)
            chunk_num  += 1
            offset     += chunk_packets
            continue

        # Build chunked tshark command
        cmd = build_tshark_cmd(pcap_path)
        # Add packet range: start at offset, read chunk_packets
        cmd.extend(['-c', str(chunk_packets)])

        # For offset > 0 we need to skip packets
        # tshark doesn't have --skip-packets so we use a filter
        if offset > 0:
            # Use frame number filter
            cmd.extend([
                '-Y',
                f'frame.number >= {offset + 1} && '
                f'frame.number <= {offset + chunk_packets}'
            ])

        print(f"  Chunk {chunk_num}: "
              f"packets {offset}-{offset + chunk_packets}...")

        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1200,   # 20 min per chunk
            )

            if result.returncode != 0:
                print(f"  [ERROR] Chunk {chunk_num}: "
                      f"{result.stderr[:200]}")
                break

            # Empty output = reached end of file
            if not result.stdout.strip() or \
               result.stdout.strip() == ','.join(TSHARK_FIELDS):
                print(f"  [DONE] Reached end of file at chunk {chunk_num}")
                break

            raw   = pd.read_csv(
                StringIO(result.stdout),
                low_memory=False,
                on_bad_lines='skip',
            )

            if len(raw) == 0:
                print(f"  [DONE] No more packets")
                break

            norm = normalize_raw(raw)
            if not norm.empty:
                save_checkpoint(norm, chunk_name)
                elapsed = round(time.time() - start, 1)
                print(f"  ✓ Chunk {chunk_num}: "
                      f"{len(norm):,} rows in {elapsed}s")
                all_chunks.append(norm)
                total_rows += len(norm)

            # If we got fewer packets than chunk size = end of file
            if len(raw) < chunk_packets:
                print(f"  [DONE] Last chunk reached")
                break

            chunk_num += 1
            offset    += chunk_packets

        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] Chunk {chunk_num} — stopping")
            break
        except Exception as e:
            print(f"  [ERROR] Chunk {chunk_num}: {e}")
            break

    print(f"  Total from {filename}: {total_rows:,} rows")

    if all_chunks:
        return pd.concat(all_chunks, ignore_index=True)
    return pd.DataFrame()


# ── Main batch processor ────────────────────────────

def run_full_extraction():
    print("=" * 60)
    print("  CIC Honeynet — Phase 2.2 Full Extraction")
    print("=" * 60)

    # Get all pcap files sorted by size (smallest first)
    all_pcaps = sorted(
        glob.glob(os.path.join(PCAP_FOLDER, '*.pcap')),
        key=os.path.getsize
    )

    print(f"\n  Found {len(all_pcaps)} .pcap files")
    print(f"  Skip list: {len(SKIP_FILES)} files")
    print(f"  Giant files: {len(GIANT_FILES)} files")
    print(f"  Checkpoints saved to: {OUTPUT_FOLDER}\n")

    # Separate into normal and giant
    normal_files = []
    giant_files  = []

    for path in all_pcaps:
        name = os.path.basename(path)
        if name in SKIP_FILES:
            print(f"  [SKIP] {name}")
            continue
        elif name in GIANT_FILES:
            giant_files.append(path)
        else:
            normal_files.append(path)

    print(f"\n  Normal files to process: {len(normal_files)}")
    print(f"  Giant files to process:  {len(giant_files)}")

    # ── Process normal files ───────────────────────
    print(f"\n{'─'*60}")
    print(f"  BATCH 1: Normal files ({len(normal_files)} files)")
    print(f"{'─'*60}")

    all_frames    = []
    total_rows    = 0
    processed     = 0
    failed        = 0

    for i, path in enumerate(normal_files):
        print(f"\n  [{i+1}/{len(normal_files)}]", end='')
        df = process_normal_file(path)

        if not df.empty:
            all_frames.append(df)
            total_rows += len(df)
            processed  += 1
        else:
            failed += 1

        # Save progress checkpoint every 5 files
        if (i + 1) % 5 == 0 and all_frames:
            interim = pd.concat(all_frames, ignore_index=True)
            interim_path = os.path.join(
                OUTPUT_FOLDER, f'interim_{i+1}.csv'
            )
            interim.to_csv(interim_path, index=False)
            print(f"\n  [CHECKPOINT] {total_rows:,} rows saved")

    print(f"\n  Batch 1 complete:")
    print(f"  Processed: {processed} files")
    print(f"  Failed:    {failed} files")
    print(f"  Rows:      {total_rows:,}")

    # ── Process giant files ────────────────────────
    if giant_files:
        print(f"\n{'─'*60}")
        print(f"  BATCH 2: Giant files ({len(giant_files)} files)")
        print(f"{'─'*60}")
        print(f"  WARNING: This may take 1-3 hours")
        print(f"  You can Ctrl+C and resume — checkpoints are saved\n")

        for path in giant_files:
            df = process_giant_file(path)
            if not df.empty:
                all_frames.append(df)
                total_rows += len(df)

    # ── Combine all extractions ────────────────────
    if not all_frames:
        print("\n[!] No data extracted")
        return

    print(f"\n{'='*60}")
    print(f"  COMBINING ALL EXTRACTIONS")
    print(f"{'='*60}")

    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.sample(frac=1, random_state=42)\
                       .reset_index(drop=True)

    combined.to_csv(FINAL_CSV, index=False)

    print(f"  Total CIC rows: {len(combined):,}")
    print(f"\n  Attack label distribution:")
    print(combined['attack_label'].value_counts().to_string())
    print(f"\n[✓] Full CIC dataset saved to: {FINAL_CSV}")
    print(f"\n  Next: run scripts/merge_cic_full.py")


if __name__ == '__main__':
    run_full_extraction()