# 1. Import Libraries
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 2. Load Dataset
df = pd.read_excel("palwinder.xlsx")

# 3. Preprocessing
# Clean column names
df.columns = df.columns.str.strip()

# Fill missing
df = df.fillna(df.mean(numeric_only=True))

# Encode categorical
# label_encoders = {}
# for col in df.select_dtypes(include=['object']).columns:
#     le = LabelEncoder()
#     df[col] = le.fit_transform(df[col])
#     label_encoders[col] = le

# Encode categorical
label_encoders = {}
for col in df.columns:
    if df[col].dtype == 'object' or df[col].dtype == 'mixed':
        
        # Convert everything to string
        df[col] = df[col].astype(str)
        
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le


# 4. Targets
target_learning = 'Learning Speed Based Category of Student'
target_behavior = 'Behavior Based Category of Student'

X = df.drop(columns=[target_learning, target_behavior])
y_learning = df[target_learning]
y_behavior = df[target_behavior]


# 5. Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 6. Context Features
def create_context_features(X):
    X = pd.DataFrame(X)
    X['engagement_index'] = X.mean(axis=1)
    X['motivation_score'] = X.std(axis=1)
    X['behavior_stability'] = X.var(axis=1)
    return X

X_context = create_context_features(X_scaled)


# 7. Train-Test Spliting
X_train, X_test, yL_train, yL_test, yB_train, yB_test = train_test_split(
    X_context, y_learning, y_behavior, test_size=0.2, random_state=42
)

# 8. IRL Reward Model
reward_model = LogisticRegression(max_iter=1000)
reward_model.fit(X_train, yB_train)
reward_weights = reward_model.coef_

def compute_reward(X):
    return np.dot(X, reward_weights.T)

# 9. Policy Models
policy_model_learning = RandomForestClassifier(n_estimators=200)
policy_model_learning.fit(X_train, yL_train)

policy_model_behavior = RandomForestClassifier(n_estimators=200)
policy_model_behavior.fit(X_train, yB_train)

# 10. Validation
pred_L = policy_model_learning.predict(X_test)
pred_B = policy_model_behavior.predict(X_test)

print("Learning Accuracy:", accuracy_score(yL_test, pred_L))
print("Behavior Accuracy:", accuracy_score(yB_test, pred_B))

print("Learning F1:", f1_score(yL_test, pred_L, average='weighted'))
print("Behavior F1:", f1_score(yB_test, pred_B, average='weighted'))

# 11. Models Saves
joblib.dump(scaler, "scaler.pkl")
joblib.dump(policy_model_learning, "learning_model.pkl")
joblib.dump(policy_model_behavior, "behavior_model.pkl")
joblib.dump(reward_weights, "reward_weights.pkl")
joblib.dump(label_encoders, "label_encoders.pkl")

print("All models saved.")