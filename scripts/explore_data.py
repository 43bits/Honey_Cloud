# scripts/explore_data.py
import pandas as pd

df = pd.read_csv(r'F:\CyberSecurity\honeycloud\datasets\AWS_Honeypot_marx-geo.csv')

print("=== DATASET SHAPE ===")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

print("\n=== COLUMN NAMES ===")
print(df.columns.tolist())

print("\n=== FIRST 3 ROWS ===")
print(df.head(3))

print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

print("\n=== UNIQUE PROTOCOLS ===")
if 'proto' in df.columns:
    print(df['proto'].value_counts())