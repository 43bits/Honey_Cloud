# ml_models/clustering.py
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os

os.makedirs('models', exist_ok=True)

CLUSTER_NAMES = {
    0: 'SSH Brute Force Campaign',
    1: 'Web Scanner Campaign',
    2: 'Database Probing Campaign',
    3: 'Credential Stuffing Campaign',
    4: 'Mass Port Scan Campaign'
}


def train_clustering():
    print("[*] Loading dataset...")
    # path=r"F:\CyberSecurity\honeycloud\datasets\AWS_Honeypot_marx-geo.csv"
    df = pd.read_csv(r"F:\CyberSecurity\honeycloud\datasets\AWS_Honeypot_marx-geo.csv")

    from ml_models.feature_engineering import engineer_features_from_dataset
    X = engineer_features_from_dataset(df)

    # Scale features (K-Means needs this)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("[*] Training K-Means with 5 clusters...")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans.fit(X_scaled)

    # Show cluster sizes
    labels = kmeans.labels_
    print("[*] Cluster distribution:")
    for i in range(5):
        count = (labels == i).sum()
        print(f"    Cluster {i} ({CLUSTER_NAMES[i]}): {count} attacks")

    # Save both model and scaler
    joblib.dump(kmeans, 'models/clustering.pkl')
    joblib.dump(scaler, 'models/cluster_scaler.pkl')
    joblib.dump(CLUSTER_NAMES, 'models/cluster_names.pkl')
    print("[+] Clustering model saved to models/clustering.pkl")

    return kmeans


# def predict_cluster(features_list):
#     """
#     features_list: output of engineer_features_from_live_log()
#     Returns: campaign name string
#     """
#     kmeans = joblib.load('models/clustering.pkl')
#     scaler = joblib.load('models/cluster_scaler.pkl')
#     names = joblib.load('models/cluster_names.pkl')

#     X_scaled = scaler.transform([features_list])
#     cluster_id = kmeans.predict(X_scaled)[0]

#     return names[cluster_id]
def predict_cluster(features_list):
    import warnings
    import numpy as np
    kmeans = joblib.load('models/clustering.pkl')
    scaler = joblib.load('models/cluster_scaler.pkl')
    names  = joblib.load('models/cluster_names.pkl')
    X      = np.array(features_list).reshape(1, -1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        X_scaled   = scaler.transform(X)
        cluster_id = int(kmeans.predict(X_scaled)[0])
    return str(names[cluster_id])

if __name__ == '__main__':
    train_clustering()