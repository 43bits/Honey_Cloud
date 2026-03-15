import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# ensure model folder exists
os.makedirs('models', exist_ok=True)


def engineer_features_from_dataset(df):
    """
    Converts raw dataset rows into ML-ready features.
    Used during TRAINING.
    """

    # clean dataset
    df = df.replace([np.inf, -np.inf], np.nan)

    features = pd.DataFrame()

    # --- Source port (attacker port) ---
    if 'spt' in df.columns:
        features['src_port'] = pd.to_numeric(df['spt'], errors='coerce').fillna(0)
    else:
        features['src_port'] = 0

    # --- Destination port (targeted service) ---
    if 'dpt' in df.columns:
        features['dst_port'] = pd.to_numeric(df['dpt'], errors='coerce').fillna(0)

    elif 'port' in df.columns:
        features['dst_port'] = pd.to_numeric(df['port'], errors='coerce').fillna(0)

    else:
        features['dst_port'] = 22


    # --- Protocol encoding ---
    proto_map = {
        'tcp': 0,
        'udp': 1,
        'icmp': 2
    }

    if 'proto' in df.columns:
        features['protocol'] = (
            df['proto']
            .astype(str)
            .str.lower()
            .map(proto_map)
            .fillna(3)
        )
    else:
        features['protocol'] = 0


    # --- Attack type encoded ---
    if 'type' in df.columns:

        le = LabelEncoder()

        attack_col = df['type'].fillna('unknown').astype(str)

        features['attack_type_encoded'] = le.fit_transform(attack_col)

        joblib.dump(le, 'models/attack_type_encoder.pkl')

    else:
        features['attack_type_encoded'] = 0


    # --- Dangerous ports ---
    dangerous_ports = [
        22, 23, 3306, 5432,
        6379, 27017, 445,
        3389, 21, 8080
    ]

    features['is_dangerous_port'] = (
        features['dst_port']
        .isin(dangerous_ports)
        .astype(int)
    )


    # --- Port category ---
    def categorize_port(p):

        if p == 22:
            return 0

        elif p in [80, 8080, 443]:
            return 1

        elif p == 21:
            return 2

        elif p == 3306:
            return 3

        elif p == 23:
            return 4

        else:
            return 5


    features['port_category'] = features['dst_port'].apply(categorize_port)


    # --- Extra cybersecurity features ---

    # high source port scanning
    features['high_port_scan'] = (
        features['src_port'] > 10000
    ).astype(int)

    # privileged port targeting
    features['privileged_port'] = (
        features['dst_port'] < 1024
    ).astype(int)


    return features



def engineer_features_from_live_log(log):
    """
    Converts LIVE honeypot logs into ML features.
    Used during real-time detection.
    """

    dst_port = log.get('port_targeted', log.get('dpt', 22))

    proto_map = {
        'tcp': 0,
        'udp': 1,
        'icmp': 2,
        'ssh': 0,
        'http': 0,
        'ftp': 0
    }

    proto_str = log.get('protocol', 'tcp').lower()

    proto_encoded = proto_map.get(proto_str, 3)

    dangerous_ports = [
        22, 23, 3306, 5432,
        6379, 27017, 445,
        3389, 21, 8080
    ]


    def categorize_port(p):

        if p == 22:
            return 0

        elif p in [80, 8080, 443]:
            return 1

        elif p == 21:
            return 2

        elif p == 3306:
            return 3

        elif p == 23:
            return 4

        else:
            return 5


    features = {
        'src_port': log.get('source_port', 0),
        'dst_port': dst_port,
        'protocol': proto_encoded,
        'attack_type_encoded': 0,
        'is_dangerous_port': 1 if dst_port in dangerous_ports else 0,
        'port_category': categorize_port(dst_port),
        'high_port_scan': 1 if log.get('source_port', 0) > 10000 else 0,
        'privileged_port': 1 if dst_port < 1024 else 0
    }

    return list(features.values())