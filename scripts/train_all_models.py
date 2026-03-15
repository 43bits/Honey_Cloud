# scripts/train_all_models.py
print("=" * 50)
print("  HoneyCloud Sentinel — Model Training")
print("=" * 50)

print("\n[1/3] Training Anomaly Detector...")
from ml_models.anomaly_detection import train_anomaly_detector
train_anomaly_detector()

print("\n[2/3] Training Attack Classifier...")
from ml_models.attack_classifier import train_classifier
train_classifier()

print("\n[3/3] Training Clustering Model...")
from ml_models.clustering import train_clustering
train_clustering()

print("\n" + "=" * 50)
print("  All models trained successfully!")
print("  Saved in: models/")
print("=" * 50)