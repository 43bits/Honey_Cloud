# ml_models/attack_classifier.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

os.makedirs('models', exist_ok=True)

ATTACK_LABELS = {
    0: 'SSH Brute Force',
    1: 'Web Exploit',
    2: 'FTP Attack',
    3: 'Database Attack',
    4: 'Telnet Attack',
    5: 'Port Scan / Other'
}

def label_attack(row):
    """
    Creates attack labels from port numbers.
    This is rule-based labeling — standard for honeypot datasets.
    """
    dpt = pd.to_numeric(row.get('dpt', row.get('port', 0)), errors='coerce') or 0

    if dpt == 22:                   return 0  # SSH Brute Force
    elif dpt in [80, 8080, 443]:    return 1  # Web Exploit
    elif dpt == 21:                 return 2  # FTP Attack
    elif dpt in [3306, 5432, 1433]: return 3  # Database Attack
    elif dpt == 23:                 return 4  # Telnet Attack
    else:                           return 5  # Port Scan / Other


def train_classifier():
    print("[*] Loading dataset...")
    # df = pd.read_csv('datasets/aws_honeypot_marx_geo.csv')
    df = pd.read_csv(r"F:\CyberSecurity\honeycloud\datasets\AWS_Honeypot_marx-geo.csv")

    from ml_models.feature_engineering import engineer_features_from_dataset
    X = engineer_features_from_dataset(df)

    print("[*] Generating labels from port analysis...")
    y = df.apply(label_attack, axis=1)

    print(f"[*] Label distribution:")
    for label_id, label_name in ATTACK_LABELS.items():
        count = (y == label_id).sum()
        print(f"    {label_name}: {count}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\n[*] Training Random Forest on {len(X_train)} samples...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    print("\n=== MODEL PERFORMANCE ===")
    print(classification_report(y_test, y_pred,
        target_names=list(ATTACK_LABELS.values())))

    # Save
    joblib.dump(clf, 'models/attack_classifier.pkl')
    joblib.dump(ATTACK_LABELS, 'models/attack_labels.pkl')
    print("[+] Classifier saved to models/attack_classifier.pkl")

    return clf


# def predict_attack_type(features_list):
#     """
#     features_list: output of engineer_features_from_live_log()
#     Returns: attack type string and confidence %
#     """
#     clf = joblib.load('models/attack_classifier.pkl')
#     labels = joblib.load('models/attack_labels.pkl')

#     prediction = clf.predict([features_list])[0]
#     probabilities = clf.predict_proba([features_list])[0]
#     confidence = round(max(probabilities) * 100, 1)

#     return labels[prediction], confidence
def predict_attack_type(features_list):
    import warnings
    import numpy as np
    clf    = joblib.load('models/attack_classifier.pkl')
    labels = joblib.load('models/attack_labels.pkl')
    X      = np.array(features_list).reshape(1, -1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        prediction    = clf.predict(X)[0]
        probabilities = clf.predict_proba(X)[0]
    confidence = round(float(max(probabilities)) * 100, 1)
    return str(labels[int(prediction)]), confidence

if __name__ == '__main__':
    train_classifier()