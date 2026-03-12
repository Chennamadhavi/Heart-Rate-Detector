# =========================================================
# HEART RATE DETECTOR with MIT-BIH + ESP32 + QSVM (Qiskit)
# =========================================================

# --- Install required libraries before running ---
# pip install numpy pandas wfdb scikit-learn qiskit qiskit-machine-learning matplotlib scipy

import wfdb
import numpy as np
import scipy.signal
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from qiskit import Aer
from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import QuantumKernel
from qiskit_machine_learning.algorithms import QSVC

# ---------------------------
# Step 1: Feature extraction
# ---------------------------
def extract_features(signal, fs=360):
    """
    Extracts heart rate related features from ECG signal:
    - BPM (Beats per minute)
    - Mean RR interval
    - Standard deviation of RR intervals
    """
    distance = int(0.6 * fs)  # Minimum distance between beats (0.6s = 100 BPM)
    peaks, _ = scipy.signal.find_peaks(signal, distance=distance, height=np.mean(signal))

    rr_intervals = np.diff(peaks) / fs  # RR intervals in seconds

    if len(rr_intervals) < 2:
        return [0, 0, 0]

    mean_rr = np.mean(rr_intervals)
    std_rr = np.std(rr_intervals)
    bpm = 60 / mean_rr

    return [bpm, mean_rr, std_rr]

# ---------------------------
# Step 2: Load MIT-BIH data
# ---------------------------
records = ['100', '101', '102']  # you can add more records from MIT-BIH
X_mitbih, y_mitbih = [], []

for rec in records:
    try:
        record = wfdb.rdrecord(rec, pn_dir='mitdb')
        annotation = wfdb.rdann(rec, 'atr', pn_dir='mitdb')
        signal = record.p_signal[:, 0]

        features = extract_features(signal)
        X_mitbih.append(features)

        # Simple labeling: N = normal (0), anything else = abnormal (1)
        label = 0 if 'N' in annotation.symbol else 1
        y_mitbih.append(label)

    except Exception as e:
        print(f"Skipping record {rec}: {e}")

X_mitbih = np.array(X_mitbih)
y_mitbih = np.array(y_mitbih)

print(f"MIT-BIH dataset loaded: {X_mitbih.shape[0]} samples")

# ----------------------------------
# Step 3: Add ESP32 heart rate data
# ----------------------------------
# Replace with real readings from your ESP32 heart rate sensor
X_esp32 = np.array([
    [78, 0.82, 0.04],   # Normal
    [122, 0.48, 0.11]   # Abnormal
])
y_esp32 = np.array([0, 1])

# Combine datasets
X = np.concatenate((X_mitbih, X_esp32), axis=0)
y = np.concatenate((y_mitbih, y_esp32), axis=0)

print("Combined dataset shape:", X.shape)

# ---------------------------------
# Step 4: Normalize the features
# ---------------------------------
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# ---------------------------------
# Step 5: Train / Test split
# ---------------------------------
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

# ---------------------------------
# Step 6: Build QSVM model
# ---------------------------------
feature_map = ZZFeatureMap(feature_dimension=X_train.shape[1], reps=2)
quantum_kernel = QuantumKernel(feature_map=feature_map, quantum_instance=Aer.get_backend('qasm_simulator'))

qsvc = QSVC(quantum_kernel=quantum_kernel)
print("Training QSVM model...")
qsvc.fit(X_train, y_train)

# ---------------------------------
# Step 7: Evaluate performance
# ---------------------------------
y_pred = qsvc.predict(X_test)
acc = accuracy_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print(f"\nModel Accuracy: {acc:.3f}")
print("Confusion Matrix:\n", cm)

# ---------------------------------
# Step 8: Real-time ESP32 reading
# ---------------------------------
new_reading = np.array([[85, 0.7, 0.06]])  # Example ESP32 live reading
new_scaled = scaler.transform(new_reading)
pred = qsvc.predict(new_scaled)

print("\nReal-Time ESP32 Reading Classification:")
print("Heart Condition:", "Normal 💚" if pred[0] == 0 else "Abnormal ❤️‍🔥")

print("\n✅ QSVM pipeline completed successfully!")
