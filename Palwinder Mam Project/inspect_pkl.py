import joblib
import sys

with open("inspect_output.txt", "w", encoding="utf-8") as f:
    try:
        scaler = joblib.load("scaler.pkl")
        f.write("Scaler features:\n")
        f.write(str(getattr(scaler, "feature_names_in_", None)) + "\n")
    except Exception as e:
        f.write("Scaler error: " + str(e) + "\n")

    try:
        encoders = joblib.load("label_encoders.pkl")
        f.write("Label encoders keys:\n")
        f.write(str(encoders.keys()) + "\n")
        for k, v in encoders.items():
            f.write(f"Encoder {k} classes: {v.classes_}\n")
    except Exception as e:
        f.write("Encoder error: " + str(e) + "\n")
