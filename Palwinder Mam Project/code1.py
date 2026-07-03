
# IMPORTS
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

import matplotlib.pyplot as plt
import seaborn as sns

# LOAD DATASET
df = pd.read_excel("palwinder.xlsx")

# CLEAN COLUMN NAMES
df.columns = df.columns.str.strip()

# HANDLE MISSING VALUES
df = df.fillna("Unknown")

# TARGET COLUMNS
target_learning = 'Learning Speed Based Category of Student'
target_behavior = 'Behavior Based Category of Student'

# SAVE RAW DATA BEFORE ENCODING
raw_df = df.copy()

# LABEL ENCODING
label_encoders = {}

for col in df.columns:

    # Convert all values to string
    df[col] = df[col].astype(str)

    le = LabelEncoder()

    df[col] = le.fit_transform(df[col])

    label_encoders[col] = le

# FEATURES & TARGETS
X = df.drop(columns=[target_learning, target_behavior])

y_learning = df[target_learning]

y_behavior = df[target_behavior]

# STANDARD SCALING
scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# CASB CONTEXT FEATURE ENGINEERING
def create_context_features(X):

    X = pd.DataFrame(X)

    # Convert column names to string
    X.columns = X.columns.astype(str)

    # CASB Features
    X['engagement_index'] = X.mean(axis=1)

    X['motivation_score'] = X.std(axis=1)

    X['behavior_stability'] = X.var(axis=1)

    return X

X_context = create_context_features(X_scaled)

# TRAIN TEST SPLIT
X_train, X_test, yL_train, yL_test, yB_train, yB_test = train_test_split(
    X_context,
    y_learning,
    y_behavior,
    test_size=0.2,
    random_state=42
)

# IRL REWARD MODEL
reward_model = LogisticRegression(max_iter=1000)

reward_model.fit(X_train, yB_train)

reward_weights = reward_model.coef_

def compute_reward(X):

    return np.dot(X, reward_weights.T)

# POLICY MODELS
learning_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

behavior_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

learning_model.fit(X_train, yL_train)

behavior_model.fit(X_train, yB_train)

# PREDICTIONS
pred_learning = learning_model.predict(X_test)

pred_behavior = behavior_model.predict(X_test)

# LEARNING MODEL METRICS
print("\n========== LEARNING MODEL ==========")

print("Accuracy:",
      accuracy_score(yL_test, pred_learning))

print("Precision:",
      precision_score(
          yL_test,
          pred_learning,
          average='weighted',
          zero_division=0
      ))

print("Recall:",
      recall_score(
          yL_test,
          pred_learning,
          average='weighted',
          zero_division=0
      ))

print("F1 Score:",
      f1_score(
          yL_test,
          pred_learning,
          average='weighted',
          zero_division=0
      ))

# BEHAVIOR MODEL METRICS
print("\n========== BEHAVIOR MODEL ==========")

print("Accuracy:",
      accuracy_score(yB_test, pred_behavior))

print("Precision:",
      precision_score(
          yB_test,
          pred_behavior,
          average='weighted',
          zero_division=0
      ))

print("Recall:",
      recall_score(
          yB_test,
          pred_behavior,
          average='weighted',
          zero_division=0
      ))

print("F1 Score:",
      f1_score(
          yB_test,
          pred_behavior,
          average='weighted',
          zero_division=0
      ))

# CONFUSION MATRIX
cm = confusion_matrix(yB_test, pred_behavior)

plt.figure(figsize=(6, 5))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')

plt.title("Behavior Prediction Confusion Matrix")

plt.xlabel("Predicted")

plt.ylabel("Actual")

plt.show()

# CASB HEATMAP
plt.figure(figsize=(10, 8))

plt.imshow(X_context.corr(), interpolation='nearest')

plt.title("CASB Context Feature Correlation Heatmap")

plt.colorbar()

plt.show()

# SAVE MODELS

joblib.dump(scaler, "scaler.pkl")

joblib.dump(learning_model, "learning_model.pkl")

joblib.dump(behavior_model, "behavior_model.pkl")

joblib.dump(reward_weights, "reward_weights.pkl")

joblib.dump(label_encoders, "label_encoders.pkl")

print("\ALL MODELS SAVED SUCCESSFULLY")

# FRONTEND PREDICTION FUNCTION
def predict_student(input_dict):

    input_df = pd.DataFrame([input_dict])

    # Clean column names
    input_df.columns = input_df.columns.str.strip()

    # Encode categorical columns
    for col in input_df.columns:

        if col in label_encoders:

            input_df[col] = input_df[col].astype(str)

            known_classes = set(label_encoders[col].classes_)

            input_df[col] = input_df[col].apply(
                lambda x: x if x in known_classes else "Unknown"
            )

            # Add Unknown class if not present
            if "Unknown" not in label_encoders[col].classes_:

                label_encoders[col].classes_ = np.append(
                    label_encoders[col].classes_,
                    "Unknown"
                )

            input_df[col] = label_encoders[col].transform(
                input_df[col]
            )

    # Scale input
    input_scaled = scaler.transform(input_df)

    # Create context features
    input_context = create_context_features(input_scaled)

    # Predictions
    learning_prediction = learning_model.predict(input_context)

    behavior_prediction = behavior_model.predict(input_context)

    reward = compute_reward(input_context)

    # Decode predictions
    learning_label = label_encoders[target_learning].inverse_transform(
        [learning_prediction[0]]
    )[0]

    behavior_label = label_encoders[target_behavior].inverse_transform(
        [behavior_prediction[0]]
    )[0]

    return {

        "learning_speed_prediction": learning_label,

        "behavior_prediction": behavior_label,

        "reward_score": float(reward[0][0])
    }

# TEST SAMPLE
sample_input = raw_df.drop(
    columns=[
        target_learning,
        target_behavior
    ]
).iloc[0].to_dict()

result = predict_student(sample_input)

print("\n========== SAMPLE OUTPUT ==========")

print(result)