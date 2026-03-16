# scripts/train_all_models.py
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# UNIFIED_PATH = 'datasets/unified_training.csv'


# cic added
# CIC_MERGED   = 'datasets/unified_training_with_cic.csv'
# UNIFIED_PATH = CIC_MERGED if os.path.exists(CIC_MERGED) \
#                else 'datasets/unified_training.csv'
               
               
               

FINAL    = 'datasets/unified_final.csv'
CIC_TEST = 'datasets/unified_training_with_cic.csv'
BASE     = 'datasets/unified_training.csv'

UNIFIED_PATH = (
    FINAL    if os.path.exists(FINAL)    else
    CIC_TEST if os.path.exists(CIC_TEST) else
    BASE
)

print(f"[*] Using dataset: {UNIFIED_PATH}")

print("=" * 55)
print("  HoneyCloud Sentinel — Multi-Dataset Model Training")
print("=" * 55)

# ── Load unified dataset ───────────────────────────
print("\n[*] Loading unified dataset...")

if not os.path.exists(UNIFIED_PATH):
    print("[!] Unified dataset not found.")
    print("[!] Run these first:")
    print("      python scripts/fix_dionaea.py")
    print("      python scripts/merge_datasets.py")
    sys.exit(1)

df = pd.read_csv(UNIFIED_PATH)
print(f"[✓] Loaded {len(df):,} rows from unified dataset")
print(f"[✓] Sources: {df['dataset_source'].value_counts().to_dict()}")
print(f"[✓] Labels:  {df['attack_label'].value_counts().to_dict()}")

# ── Feature engineering ────────────────────────────
print("\n[*] Engineering features...")
from ml_models.feature_engineering import engineer_features_from_dataset
X = engineer_features_from_dataset(df)
print(f"[✓] Feature matrix: {X.shape}")

# ── Model 1: Anomaly Detector ──────────────────────
print("\n[1/3] Training Isolation Forest (Anomaly Detector)...")
from sklearn.ensemble import IsolationForest
import joblib

anomaly_model = IsolationForest(
    n_estimators=200,     # more trees = better with larger dataset
    contamination=0.1,
    random_state=42,
    n_jobs=-1,
)
anomaly_model.fit(X)
joblib.dump(anomaly_model, 'models/anomaly_detector.pkl')
print(f"[✓] Anomaly detector trained on {len(X):,} samples")

# ── Model 2: Attack Classifier ─────────────────────
print("\n[2/3] Training Random Forest (Attack Classifier)...")
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Use attack_label column from unified dataset
y = df['attack_label'].fillna('Port Scan / Other')

# Build label map
all_labels  = sorted(y.unique())
label_map   = {label: i for i, label in enumerate(all_labels)}
index_map   = {i: label for label, i in label_map.items()}
y_encoded   = y.map(label_map)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced',  # handles imbalanced labels
)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print("\n[*] Classifier Performance:")
print(classification_report(
    y_test, y_pred,
    target_names=[index_map[i] for i in sorted(index_map.keys())]
))

joblib.dump(clf,       'models/attack_classifier.pkl')
joblib.dump(label_map, 'models/attack_labels.pkl')
joblib.dump(index_map, 'models/attack_index_map.pkl')
print(f"[✓] Classifier trained — {len(all_labels)} attack classes")

# ── Model 3: Clustering ────────────────────────────
print("\n[3/3] Training K-Means (Campaign Clustering)...")
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

scaler  = StandardScaler()
X_scaled = scaler.fit_transform(X)

# More clusters since we have more attack variety now
kmeans  = KMeans(n_clusters=8, random_state=42, n_init=10)
kmeans.fit(X_scaled)

# Auto-name clusters from dominant label in each
df['cluster'] = kmeans.labels_
cluster_names = {}
for cid in range(8):
    mask      = df['cluster'] == cid
    if mask.sum() == 0:
        cluster_names[cid] = f'Cluster {cid}'
        continue
    top_label = df.loc[mask, 'attack_label'].mode()[0]
    count     = mask.sum()
    cluster_names[cid] = f'{top_label} Campaign ({count:,} events)'

print("[*] Cluster composition:")
for cid, name in cluster_names.items():
    print(f"    Cluster {cid}: {name}")

joblib.dump(kmeans,        'models/clustering.pkl')
joblib.dump(scaler,        'models/cluster_scaler.pkl')
joblib.dump(cluster_names, 'models/cluster_names.pkl')
print(f"[✓] Clustering trained — 8 campaign clusters")

# ── Summary ────────────────────────────────────────
print(f"\n{'='*55}")
print(f"  ALL MODELS TRAINED SUCCESSFULLY")
print(f"{'='*55}")
print(f"  Training dataset: {len(df):,} attacks")
print(f"  Sources: AWS Honeypot + Dionaea Honeypot")
print(f"  Attack classes: {len(all_labels)}")
print(f"  Campaign clusters: 8")
print(f"  Models saved to: models/")
print(f"{'='*55}")