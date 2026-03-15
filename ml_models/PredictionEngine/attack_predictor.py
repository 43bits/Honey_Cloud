# ml_models/attack_predictor.py
import numpy as np
import os
import joblib
from collections import deque

os.makedirs('models', exist_ok=True)

# Attack type to integer mapping
ATTACK_CLASSES = {
    'SSH Brute Force':    0,
    'Web Exploit':        1,
    'Database Attack':    2,
    'FTP Attack':         3,
    'Port Scan / Other':  4,
    'Telnet Attack':      5,
}
INDEX_TO_CLASS = {v: k for k, v in ATTACK_CLASSES.items()}

# Sequence length — how many past attacks to look at
SEQ_LENGTH = 10


def encode_attacks(attack_types: list) -> np.ndarray:
    """Convert attack type strings to integer indices."""
    return np.array([
        ATTACK_CLASSES.get(a, 4)
        for a in attack_types
    ])


def build_sequences(encoded: np.ndarray):
    """Build X, y pairs from encoded sequence."""
    X, y = [], []
    for i in range(len(encoded) - SEQ_LENGTH):
        X.append(encoded[i: i + SEQ_LENGTH])
        y.append(encoded[i + SEQ_LENGTH])
    return np.array(X), np.array(y)


def train_lstm(attack_types: list) -> None:
    """
    Train LSTM on a list of attack type strings.
    Saves model and encoder to models/ folder.
    """
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import (
        LSTM, Dense, Embedding, Dropout
    )
    from tensorflow.keras.utils import to_categorical

    print("[LSTM] Encoding attack sequences...")
    encoded = encode_attacks(attack_types)
    X, y    = build_sequences(encoded)

    if len(X) < 10:
        print("[LSTM] Not enough data to train — need 20+ attacks")
        return

    num_classes = len(ATTACK_CLASSES)
    y_cat       = to_categorical(y, num_classes=num_classes)

    print(f"[LSTM] Training on {len(X)} sequences...")

    model = Sequential([
        Embedding(
            input_dim=num_classes,
            output_dim=16,
            input_length=SEQ_LENGTH
        ),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(num_classes, activation='softmax'),
    ])

    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    model.fit(
        X, y_cat,
        epochs=30,
        batch_size=8,
        validation_split=0.2,
        verbose=1,
    )

    model.save('models/lstm_predictor.keras')
    joblib.dump(ATTACK_CLASSES, 'models/attack_classes.pkl')
    print("[LSTM] Model saved to models/lstm_predictor.keras")


def predict_next_attack(recent_attacks: list) -> dict:
    """
    Given last N attack types, predict the next one.
    recent_attacks: list of attack type strings (newest last)
    Returns: dict with prediction, confidence, recommendation
    """
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(
            'models/lstm_predictor.keras'
        )
    except Exception:
        return {
            'predicted':      'Unknown',
            'confidence':     0.0,
            'probabilities':  {},
            'ready':          False,
            'reason':         'Model not trained yet',
        }

    # Take last SEQ_LENGTH attacks
    window = recent_attacks[-SEQ_LENGTH:]

    # Pad if not enough history
    while len(window) < SEQ_LENGTH:
        window = ['Port Scan / Other'] + window

    encoded = encode_attacks(window)
    X       = encoded.reshape(1, SEQ_LENGTH)

    probs      = model.predict(X, verbose=0)[0]
    top_idx    = int(np.argmax(probs))
    confidence = float(round(probs[top_idx] * 100, 1))

    predicted  = INDEX_TO_CLASS.get(top_idx, 'Unknown')

    # All class probabilities
    all_probs = {
        INDEX_TO_CLASS[i]: round(float(probs[i]) * 100, 1)
        for i in range(len(probs))
    }

    return {
        'predicted':     predicted,
        'confidence':    confidence,
        'probabilities': all_probs,
        'ready':         True,
        'sequence_used': window,
    }


def get_recommendation(predicted: str, confidence: float) -> str:
    """Return a preemptive action based on prediction."""
    recs = {
        'SSH Brute Force': (
            'Preemptively rate-limit SSH connections. '
            'Enable fail2ban if not active.'
        ),
        'Web Exploit': (
            'Review WAF rules. Check for unpatched CVEs '
            'in web-facing applications.'
        ),
        'Database Attack': (
            'Verify DB ports are firewalled. '
            'Rotate database credentials now.'
        ),
        'FTP Attack': (
            'Disable anonymous FTP. Switch to SFTP '
            'for all file transfers.'
        ),
        'Port Scan / Other': (
            'Enable network scan detection. '
            'Review exposed service inventory.'
        ),
        'Telnet Attack': (
            'Disable Telnet immediately. '
            'Block port 23 at perimeter firewall.'
        ),
    }
    base = recs.get(predicted, 'Monitor all services closely.')
    if confidence > 80:
        return f'HIGH CONFIDENCE — {base}'
    elif confidence > 60:
        return f'MEDIUM CONFIDENCE — {base}'
    else:
        return f'LOW CONFIDENCE — {base} Continue monitoring.'# Last 10 attacks in sequence
#         ↓
# LSTM Neural Network
#         ↓
# Predicts next likely attack type
# + confidence score
# + recommended preemptive action
#         ↓
# Dashboard shows prediction panel
# "Next likely attack: Database Attack (78% confidence)"

