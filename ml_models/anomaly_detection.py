# ml_models/anomaly_detection.py
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
import joblib
import os

os.makedirs('models', exist_ok=True)
path = r"F:\CyberSecurity\honeycloud\datasets\AWS_Honeypot_marx-geo.csv"
def train_anomaly_detector():
    print("[*] Loading dataset...")
    # df = pd.read_csv('datasets/Aws_Honeypot_marx_geo.csv')
    df = pd.read_csv(r"F:\CyberSecurity\honeycloud\datasets\AWS_Honeypot_marx-geo.csv")
    # Import our feature engineering
    from ml_models.feature_engineering import engineer_features_from_dataset
    X = engineer_features_from_dataset(df)

    print(f"[*] Training on {len(X)} samples...")

    model = IsolationForest(
        n_estimators=100,
        contamination=0.1,   # assumes 10% of data is anomalous
        random_state=42,
        n_jobs=-1
    )
    model.fit(X)

    # Save model
    joblib.dump(model, 'models/anomaly_detector.pkl')
    print("[+] Anomaly detector saved to models/anomaly_detector.pkl")

    # Quick test
    sample = X.iloc[:5]
    predictions = model.predict(sample)
    print(f"[*] Sample predictions (1=normal, -1=anomaly): {predictions}")

    return model


# def predict_anomaly(features_list):
#     """
#     features_list: output of engineer_features_from_live_log()
#     Returns: True if anomaly, False if normal
#     """
#     model = joblib.load('models/anomaly_detector.pkl')
#     result = model.predict([features_list])[0]
#     score = model.decision_function([features_list])[0]
#     return result == -1, round(score, 4)
def predict_anomaly(features_list):
    import warnings
    import numpy as np
    model = joblib.load('models/anomaly_detector.pkl')
    X = np.array(features_list).reshape(1, -1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = model.predict(X)[0]
        score  = model.decision_function(X)[0]
    return bool(result == -1), float(score)

if __name__ == '__main__':
    train_anomaly_detector()