# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import LabelEncoder
# import joblib
# import os

# # ensure model folder exists
# os.makedirs('models', exist_ok=True)


# # def engineer_features_from_dataset(df):
# #     """
# #     Converts raw dataset rows into ML-ready features.
# #     Used during TRAINING.
# #     """

# #     # clean dataset
# #     df = df.replace([np.inf, -np.inf], np.nan)

# #     features = pd.DataFrame()

# #     # --- Source port (attacker port) ---
# #     if 'spt' in df.columns:
# #         features['src_port'] = pd.to_numeric(df['spt'], errors='coerce').fillna(0)
# #     else:
# #         features['src_port'] = 0

# #     # --- Destination port (targeted service) ---
# #     if 'dpt' in df.columns:
# #         features['dst_port'] = pd.to_numeric(df['dpt'], errors='coerce').fillna(0)

# #     elif 'port' in df.columns:
# #         features['dst_port'] = pd.to_numeric(df['port'], errors='coerce').fillna(0)

# #     else:
# #         features['dst_port'] = 22


# #     # --- Protocol encoding ---
# #     proto_map = {
# #         'tcp': 0,
# #         'udp': 1,
# #         'icmp': 2
# #     }

# #     if 'proto' in df.columns:
# #         features['protocol'] = (
# #             df['proto']
# #             .astype(str)
# #             .str.lower()
# #             .map(proto_map)
# #             .fillna(3)
# #         )
# #     else:
# #         features['protocol'] = 0


# #     # --- Attack type encoded ---
# #     if 'type' in df.columns:

# #         le = LabelEncoder()

# #         attack_col = df['type'].fillna('unknown').astype(str)

# #         features['attack_type_encoded'] = le.fit_transform(attack_col)

# #         joblib.dump(le, 'models/attack_type_encoder.pkl')

# #     else:
# #         features['attack_type_encoded'] = 0


# #     # --- Dangerous ports ---
# #     dangerous_ports = [
# #         22, 23, 3306, 5432,
# #         6379, 27017, 445,
# #         3389, 21, 8080
# #     ]

# #     features['is_dangerous_port'] = (
# #         features['dst_port']
# #         .isin(dangerous_ports)
# #         .astype(int)
# #     )


# #     # --- Port category ---
# #     def categorize_port(p):

# #         if p == 22:
# #             return 0

# #         elif p in [80, 8080, 443]:
# #             return 1

# #         elif p == 21:
# #             return 2

# #         elif p == 3306:
# #             return 3

# #         elif p == 23:
# #             return 4

# #         else:
# #             return 5


# #     features['port_category'] = features['dst_port'].apply(categorize_port)


# #     # --- Extra cybersecurity features ---

# #     # high source port scanning
# #     features['high_port_scan'] = (
# #         features['src_port'] > 10000
# #     ).astype(int)

# #     # privileged port targeting
# #     features['privileged_port'] = (
# #         features['dst_port'] < 1024
# #     ).astype(int)


# #     return features



# # ml_models/feature_engineering.py  — UPDATE this function for new data set
# def engineer_features_from_dataset(df):
#     """
#     Works with the unified dataset (AWS + Dionaea).
#     """
#     features = pd.DataFrame()

#     # Source port
#     features['src_port'] = pd.to_numeric(
#         df.get('src_port', 0), errors='coerce'
#     ).fillna(0).astype(int)

#     # Destination port
#     features['dst_port'] = pd.to_numeric(
#         df.get('dst_port', df.get('dpt', 0)),
#         errors='coerce'
#     ).fillna(0).astype(int)

#     # Protocol
#     proto_map = {'TCP': 0, 'UDP': 1, 'ICMP': 2}
#     features['protocol'] = df.get('protocol', df.get('proto', 'TCP'))\
#         .str.upper().map(proto_map).fillna(3).astype(int)

#     # Dataset source (new feature — helps model learn dataset patterns)
#     source_map = {'aws': 0, 'dionaea': 1, 'hornet40': 2}
#     if 'dataset_source' in df.columns:
#         features['dataset_source'] = df['dataset_source']\
#             .map(source_map).fillna(0).astype(int)
#     else:
#         features['dataset_source'] = 0

#     # Is dangerous port
#     dangerous_ports = [22, 23, 3306, 5432, 6379,
#                        27017, 445, 3389, 21, 8080,
#                        1433, 9200, 5984, 135, 139]
#     features['is_dangerous_port'] = features['dst_port']\
#         .isin(dangerous_ports).astype(int)

#     # Port category
#     def categorize_port(p):
#         if p == 22:                      return 0  # SSH
#         elif p in [80, 8080, 443, 8443]: return 1  # HTTP
#         elif p == 21:                    return 2  # FTP
#         elif p in [3306, 5432, 1433]:    return 3  # DB
#         elif p == 23:                    return 4  # Telnet
#         elif p in [445, 135, 139]:       return 5  # SMB
#         elif p in [25, 587, 465]:        return 6  # Email
#         elif p == 53:                    return 7  # DNS
#         else:                            return 8  # Other

#     features['port_category'] = features['dst_port']\
#         .apply(categorize_port).astype(int)

#     return features


# # def engineer_features_from_live_log(log):
# #     """
# #     Converts LIVE honeypot logs into ML features.
# #     Used during real-time detection.
# #     """

# #     dst_port = log.get('port_targeted', log.get('dpt', 22))

# #     proto_map = {
# #         'tcp': 0,
# #         'udp': 1,
# #         'icmp': 2,
# #         'ssh': 0,
# #         'http': 0,
# #         'ftp': 0
# #     }

# #     proto_str = log.get('protocol', 'tcp').lower()

# #     proto_encoded = proto_map.get(proto_str, 3)

# #     dangerous_ports = [
# #         22, 23, 3306, 5432,
# #         6379, 27017, 445,
# #         3389, 21, 8080
# #     ]


# #     def categorize_port(p):

# #         if p == 22:
# #             return 0

# #         elif p in [80, 8080, 443]:
# #             return 1

# #         elif p == 21:
# #             return 2

# #         elif p == 3306:
# #             return 3

# #         elif p == 23:
# #             return 4

# #         else:
# #             return 5


# #     features = {
# #         'src_port': log.get('source_port', 0),
# #         'dst_port': dst_port,
# #         'protocol': proto_encoded,
# #         'attack_type_encoded': 0,
# #         'is_dangerous_port': 1 if dst_port in dangerous_ports else 0,
# #         'port_category': categorize_port(dst_port),
# #         'high_port_scan': 1 if log.get('source_port', 0) > 10000 else 0,
# #         'privileged_port': 1 if dst_port < 1024 else 0
# #     }

# #     return list(features.values())


# def engineer_features_from_live_log(log: dict) -> list:
#     """
#     Converts a single LIVE log dict (from Kafka) into ML features.
#     Must produce EXACTLY the same 8 features as engineer_features_from_dataset.
#     """
#     dst_port   = int(log.get('port_targeted', log.get('dpt', 22)) or 22)
#     src_port   = int(log.get('source_port',   log.get('spt', 0))  or 0)

#     proto_map  = {'tcp': 0, 'udp': 1, 'icmp': 2,
#                   'ssh': 0, 'http': 0, 'ftp': 0, 'TCP': 0,
#                   'UDP': 1, 'ICMP': 2}
#     proto_str  = str(log.get('protocol', 'tcp')).lower()
#     proto_enc  = proto_map.get(proto_str, 3)

#     # Dataset source — live data is always 0 (aws-like)
#     dataset_source = 0

#     dangerous_ports = [
#         22, 23, 3306, 5432, 6379, 27017,
#         445, 3389, 21, 8080, 1433, 9200,
#         5984, 135, 139, 25, 587, 53,
#     ]
#     is_dangerous = 1 if dst_port in dangerous_ports else 0

#     def categorize_port(p):
#         if p == 22:                         return 0  # SSH
#         elif p in [80, 8080, 443, 8443]:    return 1  # HTTP
#         elif p == 21:                       return 2  # FTP
#         elif p in [3306, 5432, 1433]:       return 3  # DB
#         elif p == 23:                       return 4  # Telnet
#         elif p in [445, 135, 139]:          return 5  # SMB
#         elif p in [25, 587, 465]:           return 6  # Email
#         elif p == 53:                       return 7  # DNS
#         else:                               return 8  # Other

#     # MUST be same order as engineer_features_from_dataset
#     return [
#         src_port,           # feature 1
#         dst_port,           # feature 2
#         proto_enc,          # feature 3
#         dataset_source,     # feature 4 ← new
#         is_dangerous,       # feature 5
#         categorize_port(dst_port),  # feature 6
#         0,                  # feature 7 — attack_type_encoded (unknown live)
#         0,                  # feature 8 — placeholder
#     ]



# ml_models/feature_engineering.py
import pandas as pd
import numpy as np
import joblib
import os

os.makedirs('models', exist_ok=True)

# ── Port helpers ───────────────────────────────────

DANGEROUS_PORTS = [
    22, 23, 3306, 5432, 6379, 27017, 445,
    3389, 21, 8080, 1433, 9200, 5984,
    135, 139, 25, 587, 465, 53,
]

def categorize_port(p: int) -> int:
    p = int(p)
    if p == 22:                      return 0   # SSH
    elif p in [80, 8080, 443, 8443]: return 1   # HTTP
    elif p == 21:                    return 2   # FTP
    elif p in [3306, 5432, 1433,
               27017, 6379, 9200]:   return 3   # Database
    elif p == 23:                    return 4   # Telnet
    elif p in [445, 135, 139]:       return 5   # SMB
    elif p in [25, 587, 465]:        return 6   # Email
    elif p == 53:                    return 7   # DNS
    else:                            return 8   # Other

PROTO_MAP = {
    'tcp': 0, 'TCP': 0,
    'udp': 1, 'UDP': 1,
    'icmp': 2, 'ICMP': 2,
}

SOURCE_MAP = {'aws': 0, 'dionaea': 1, 'hornet40': 2}

# ── FEATURE NAMES — single source of truth ─────────
# Both training and live functions must produce these
# 7 features in this exact order.
FEATURE_NAMES = [
    'src_port',
    'dst_port',
    'protocol',
    'dataset_source',
    'is_dangerous_port',
    'port_category',
    'is_high_port',        # src_port > 1024 (common for scanners)
]
N_FEATURES = len(FEATURE_NAMES)  # 7


def _build_row(src_port: int, dst_port: int,
               proto: int, source: int) -> list:
    """Core feature builder — called by both functions."""
    return [
        int(src_port),
        int(dst_port),
        int(proto),
        int(source),
        1 if dst_port in DANGEROUS_PORTS else 0,
        categorize_port(dst_port),
        1 if src_port > 1024 else 0,
    ]


# ── Training function ──────────────────────────────

def engineer_features_from_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts unified dataset rows into ML-ready features.
    Called during model training.
    Returns a DataFrame with FEATURE_NAMES columns.
    """
    src_port = pd.to_numeric(
        df.get('src_port', 0), errors='coerce'
    ).fillna(0).astype(int)

    dst_port = pd.to_numeric(
        df.get('dst_port', df.get('dpt', 0)),
        errors='coerce'
    ).fillna(0).astype(int)

    protocol = df.get('protocol', df.get('proto', 'tcp'))\
        .astype(str).str.lower()\
        .map({'tcp': 0, 'udp': 1, 'icmp': 2})\
        .fillna(3).astype(int)

    if 'dataset_source' in df.columns:
        source = df['dataset_source']\
            .map(SOURCE_MAP).fillna(0).astype(int)
    else:
        source = pd.Series([0] * len(df))

    features = pd.DataFrame({
        'src_port':          src_port,
        'dst_port':          dst_port,
        'protocol':          protocol,
        'dataset_source':    source,
        'is_dangerous_port': dst_port.isin(DANGEROUS_PORTS).astype(int),
        'port_category':     dst_port.apply(categorize_port).astype(int),
        'is_high_port':      (src_port > 1024).astype(int),
    })

    return features[FEATURE_NAMES]


# ── Live function ──────────────────────────────────

def engineer_features_from_live_log(log: dict) -> list:
    """
    Converts a single LIVE attack log into ML features.
    Must return EXACTLY N_FEATURES values in FEATURE_NAMES order.
    Called during real-time prediction.
    """
    src_port = int(log.get('source_port', log.get('spt', 0)) or 0)
    dst_port = int(log.get('port_targeted', log.get('dpt', 22)) or 22)

    proto_raw = str(log.get('protocol', 'tcp')).lower().strip()
    proto_enc = PROTO_MAP.get(proto_raw, 0)

    # Live data treated as aws-like source
    source = 0

    row = _build_row(src_port, dst_port, proto_enc, source)

    assert len(row) == N_FEATURES, (
        f"Feature count mismatch: got {len(row)}, expected {N_FEATURES}"
    )
    return row