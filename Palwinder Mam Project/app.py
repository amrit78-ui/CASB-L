
# CASB-IRL FINAL FLASK APP
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

import pandas as pd
import numpy as np
import joblib
import sqlite3
import shap
from datetime import datetime
import json

# FLASK SETUP
app = Flask(__name__)

CORS(app)

# LOAD MODELS
scaler = joblib.load("scaler.pkl")

learning_model = joblib.load("learning_model.pkl")

behavior_model = joblib.load("behavior_model.pkl")

reward_weights = joblib.load("reward_weights.pkl")

label_encoders = joblib.load("label_encoders.pkl")

# TARGET COLUMN NAMES

target_learning = 'Learning Speed Based Category of Student'

target_behavior = 'Behavior Based Category of Student'

EXPECTED_COLUMNS = [
    'Timestamp', 'Email address', '⁸Name of the Student', 'Gender', 'Age',
    'Nationality', 'Religion', 'Admission Year', 'Program / Course', 'Semester',
    'Duration of the Couse (In years )', 'Study Time in One Day(In Hours)',
    'Play Time in One Day (In Hours)', 'Free Time in One Day(In Hours)',
    'Current Attendance Percentage (Overall)', 'Stress Level',
    'Socializing with Friends', 'Hours of Sleep (In hours)',
    'Parental Encouragement', 'Living with Parents, Hostel or PG',
    'Living City or Location',
    'Interest in class subjects (Tell subject name in which you are interested), \nIf yes( write the subject name) , If no (write no)',
    'Level of difficulty of subjects', 'Test Anxiety', 'Critical Thinking',
    'Family Size',
    'Family Income Level (Low (₹1.5 lakh to ₹4 lakh)/ Medium (₹4 lakh to ₹20 lakh) / High (>₹15 lakh))',
    "Mother's level of Education", "Father's level of Education",
    'Father Career', 'Mother Career', 'Parent Status', 'No of Brothers/ Sisters',
    'Position as child', 'Previous Class Percentage (In percentage)',
    'Health Status', 'Studying in group', 'Transport method used',
    'Distance of Educational Institution (In KM.)', 'Skill',
    'Total Hours of Class in One Week (In Hours)',
    'Extra Time Utilization (In Hours)', 'Way of Homework',
    'Timely Submission of Assignments and Homework',
    'Special Education needs depending on the disability',
    'Class Participation Frequency', 'Discipline History', 'Note-taking Habits',
    'Absenteeism History', 'Peer Interactions', 'Number of Friends',
    'Participation in Group Activities', 'Response to Feedback / Criticism',
    'Question-Asking Frequency', 'Help-Seeking Behavior', 'Leadership Roles',
    'Sports Involvement', 'Volunteer Activities',
    'Level of Boredom During Classes',
    'Having a Personal Tutor or go for Tuition?',
    'Contents of the Course are Interesting',
    'Enjoy Mobile Devices for Learning',
    'Time Spent on Social Media (In Hours)', 'Food Preference',
    'University Name / Board Name',
    'Write Name if having any Physical Disability or Suffering a Critical Issue'
]

# DATABASE SETUP
conn = sqlite3.connect("students.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learning_prediction TEXT,
    behavior_prediction TEXT,
    behavior_sentiment TEXT,
    reward_score REAL,
    student_name TEXT DEFAULT 'Unknown',
    timestamp TEXT
)
""")

conn.commit()

# Ensure behavior_sentiment column exists in case of an older database
try:
    cursor.execute("ALTER TABLE predictions ADD COLUMN behavior_sentiment TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

# CASB CONTEXT FEATURES
def create_context_features(X):

    X = pd.DataFrame(X)
    X.columns = X.columns.astype(str)

    X['engagement_index'] = X.mean(axis=1)

    X['motivation_score'] = X.std(axis=1)

    X['behavior_stability'] = X.var(axis=1)

    return X

# COMPUTE REWARD
def compute_reward(X):

    return np.dot(X, reward_weights.T)

# GENERATE RECOMMENDATIONS
def generate_recommendations(learning_label, behavior_label, input_data):
    recs = []

    # Helper: safe numeric fetch
    def num(key, default=0):
        try:
            return float(input_data.get(key, default) or default)
        except:
            return default

    def val(key):
        return str(input_data.get(key, "") or "").strip().lower()

    # LEARNING SPEED 
    if "slow" in learning_label.lower():
        recs.append("Break study sessions into focused 25-min Pomodoro blocks with 5-min breaks to boost retention.")
        recs.append("Join a peer study group - collaborative learning accelerates understanding of difficult topics.")
        recs.append("Practice active recall and spaced repetition instead of passive reading for stronger memory.")

    if "average" in learning_label.lower():
        recs.append("You're on the right track! Push further by reviewing lecture notes within 24 hours of class.")
        recs.append("Try teaching concepts to a friend or writing summaries - it solidifies your understanding.")

    if "fast" in learning_label.lower():
        recs.append("Excellent learning pace! Consider mentoring peers to deepen your own mastery.")
        recs.append("Explore advanced resources, research papers, or online certifications to stay ahead.")

    # BEHAVIOR 
    if "negative" in behavior_label.lower():
        recs.append("Practice 10 minutes of mindfulness or deep breathing daily to improve emotional regulation.")
        recs.append("Consider speaking to a counselor or mentor about the challenges affecting your behavior.")

    if "stress" in behavior_label.lower() or val("Stress Level") == "severe stress":
        recs.append("High stress detected! Schedule at least 30 minutes of physical activity 3× per week.")
        recs.append("Maintain a daily journal to track stressors and identify patterns you can address.")

    if val("Stress Level") == "mild stress":
        recs.append("Mild stress noted. Build a realistic weekly schedule to balance study and leisure time.")

    # SLEEP 
    sleep = num("Hours of Sleep (In hours)")
    if 0 < sleep < 6:
        recs.append("Critical: You're sleeping less than 6 hours. Aim for 7-9 hours — sleep is vital for memory consolidation.")
    elif sleep == 6:
        recs.append("Try adding 1 more hour of sleep. Research shows 7+ hours improves test performance significantly.")
    elif sleep >= 9:
        recs.append("Oversleeping can reduce productivity. Try maintaining a consistent 7–8 hour schedule.")

    # SOCIAL MEDIA 
    social = num("Time Spent on Social Media (In Hours)")
    if social > 4:
        recs.append("You spend 4+ hours on social media daily. Use app timers to limit usage to under 1.5 hours.")
    elif social > 2:
        recs.append("Moderate social media use detected. Avoid screens 30 minutes before bed to improve sleep quality.")

    # STUDY TIME 
    study = num("Study Time in One Day(In Hours)")
    if study < 2:
        recs.append("Studying under 2 hours/day is insufficient. Gradually increase to at least 3-4 focused hours.")
    elif study > 8:
        recs.append("Studying 8+ hours risks burnout. Include regular breaks and leisure to maintain long-term performance.")

    # ATTENDANCE 
    attendance = num("Current Attendance Percentage (Overall)")
    if 0 < attendance < 75:
        recs.append("Attendance below 75% is critical! Regular attendance directly correlates with academic performance.")
    elif 75 <= attendance < 85:
        recs.append("Try to improve attendance above 90%. Missing classes creates knowledge gaps that are hard to recover.")

    # CLASS PARTICIPATION 
    if val("Class Participation Frequency") == "low":
        recs.append("Participate more in class! Even asking one question per lecture boosts engagement and understanding.")

    #  NOTE-TAKING 
    if val("Note-taking Habits") in ["rarely", "never", "no"]:
        recs.append("Start taking structured notes using the Cornell Method or mind maps — they improve recall by 40%.")

    # HOMEWORK & ASSIGNMENTS 
    if val("Timely Submission of Assignments and Homework") in ["no", "rarely", "late"]:
        recs.append("Timely submissions matter! Use a planner or task app to track deadlines and avoid last-minute rushes.")

    # TUTOR / EXTRA HELP 
    if val("Having a Personal Tutor or go for Tuition?") == "no" and "slow" in learning_label.lower():
        recs.append("Consider enrolling in tutoring or coaching classes for subjects where you feel weak.")

    # PLAY / FREE TIME 
    play = num("Play Time in One Day (In Hours)")
    if play > 4:
        recs.append("High play time detected. Balance recreation with academics to maintain a healthy study ratio.")
    elif play == 0:
        recs.append("Don't skip recreation! At least 30–60 minutes of play/exercise daily boosts brain performance.")

    # PEER INTERACTIONS 
    if val("Peer Interactions") == "negative" or val("Peer Interactions") == "low":
        recs.append("Work on building positive peer relationships - a supportive social circle improves motivation.")

    # DISCIPLINE 
    if val("Discipline History") in ["poor", "bad", "negative"]:
        recs.append("Focus on self-discipline. Set small daily goals and reward yourself when you achieve them.")

    # BOREDOM IN CLASS 
    if val("Level of Boredom During Classes") == "high":
        recs.append("High classroom boredom noted. Try actively linking lesson content to real-world applications to stay engaged.")

    # PARENTAL ENCOURAGEMENT 
    if val("Parental Encouragement") == "no":
        recs.append("Even without strong parental support, self-motivation is powerful. Connect with a mentor or counselor.")

    # HEALTH 
    if val("Health Status") != "healthy person" and val("Health Status") != "":
        recs.append("Your health condition may impact studies. Work with your institution for academic accommodations if needed.")

    # POSITIVE FALLBACK 
    if len(recs) == 0:
        recs.append("Outstanding profile! Keep maintaining your excellent study habits and positive attitude.")
        recs.append("Consider taking on leadership roles in clubs or projects to further develop your potential.")
        recs.append("Explore internships or research opportunities to apply your learning practically.")

    # Always cap at 8 most relevant
    return recs[:8]

# BATCH PREDICTION IMPORTS
import os
import uuid
from werkzeug.utils import secure_filename
from flask import send_from_directory

EXPORTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

# PREDICT BATCH FOR CSV UPLOAD
def predict_batch(df):
    # 1. Clean column names
    df.columns = df.columns.astype(str).str.strip()
    
    # 2. Map dataframe columns to EXPECTED_COLUMNS
    col_map = {}
    for actual_col in df.columns:
        actual_clean = str(actual_col).replace('\n', ' ').strip().lower()
        # Remove special character ⁸ if present in check
        actual_clean = actual_clean.replace('⁸', '')
        for exp_col in EXPECTED_COLUMNS:
            exp_clean = exp_col.replace('\n', ' ').strip().lower()
            exp_clean = exp_clean.replace('⁸', '')
            if actual_clean == exp_clean or actual_clean.endswith(exp_clean) or exp_clean.endswith(actual_clean):
                col_map[actual_col] = exp_col
                break
    
    df = df.rename(columns=col_map)
    
    # Reindex/pad missing columns with "Unknown" or default values
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = "Unknown"
            
    # Select only EXPECTED_COLUMNS in correct order
    df_features = df[EXPECTED_COLUMNS].copy()
    
    # 3. Label Encoding
    for col in df_features.columns:
        df_features[col] = df_features[col].astype(str).str.strip()
        if col in label_encoders:
            known_classes = set(label_encoders[col].classes_)
            
            if "Unknown" not in known_classes:
                label_encoders[col].classes_ = np.append(label_encoders[col].classes_, "Unknown")
                
            df_features[col] = df_features[col].apply(lambda x: x if x in known_classes else "Unknown")
            df_features[col] = label_encoders[col].transform(df_features[col])
        else:
            df_features[col] = pd.to_numeric(df_features[col], errors='coerce').fillna(0)
            
    # 4. Standard Scaling
    features_scaled = scaler.transform(df_features)
    
    # 5. Context Features
    features_context = create_context_features(features_scaled)
    
    # 6. Predict Batch
    learning_preds = learning_model.predict(features_context)
    behavior_preds = behavior_model.predict(features_context)
    rewards = compute_reward(features_context)
    
    # 7. Decode Predictions
    learning_labels = label_encoders[target_learning].inverse_transform(learning_preds)
    behavior_labels = label_encoders[target_behavior].inverse_transform(behavior_preds)
    reward_scores = rewards.flatten()
    
    return learning_labels, behavior_labels, reward_scores

# HOME ROUTE
@app.route('/')

def home():

    return render_template("index.html")

@app.route('/form')

def form_page():

    return render_template("form.html")

# PREDICTION ROUTE
@app.route('/predict', methods=['POST'])

def predict():

    try:

        data = request.json

        # Initialize a dictionary with "Unknown" for all expected columns
        input_data = {col: "Unknown" for col in EXPECTED_COLUMNS}
        
        # Override with any data provided from frontend
        for key, value in data.items():
            if key in input_data and str(value).strip() != "":
                input_data[key] = str(value).strip()
        
        # Ensure we create the DataFrame with EXACTLY the expected columns in the right order
        input_df = pd.DataFrame([input_data], columns=EXPECTED_COLUMNS)

        # Encode categorical columns
        for col in input_df.columns:

            if col in label_encoders:
                val = input_df[col].iloc[0]
                
                # Check if it exists in known classes
                known_classes = set(label_encoders[col].classes_)
                
                if val not in known_classes:
                    # Fallback to "Unknown" if it's new
                    val = "Unknown"
                    if "Unknown" not in known_classes:
                        # Append "Unknown" if it isn't in classes either
                        label_encoders[col].classes_ = np.append(
                            label_encoders[col].classes_, "Unknown"
                        )
                
                input_df[col] = label_encoders[col].transform([val])
            
            else:
                # If there are numerical columns without label encoders (though training did all as label encoders)
                input_df[col] = pd.to_numeric(input_df[col], errors='coerce').fillna(0)

        # Scale
        input_scaled = scaler.transform(input_df)

        # Context Features
        input_context = create_context_features(input_scaled)

        # Predictions
        learning_prediction = learning_model.predict(input_context)

        behavior_prediction = behavior_model.predict(input_context)

        reward = compute_reward(input_context)

        # Decode Predictions
        learning_label = label_encoders[target_learning].inverse_transform(
            [learning_prediction[0]]
        )[0]

        behavior_label = label_encoders[target_behavior].inverse_transform(
            [behavior_prediction[0]]
        )[0]

        reward_score = float(reward[0][0])

        # Generate Recommendations
        recommendations = generate_recommendations(learning_label, behavior_label, input_data)

        # SHAP Explainability
        # Use TreeExplainer for Random Forest
        explainer = shap.TreeExplainer(learning_model)
        shap_values = explainer.shap_values(input_context)
        
        # shap_values for RF is a list of arrays (one for each class). 
        # We get the index of the predicted class to find its specific SHAP values
        predicted_class_idx = learning_prediction[0]
        # In newer SHAP versions, shap_values might be a 3D array or a list.
        if isinstance(shap_values, list):
            class_shap_values = shap_values[predicted_class_idx][0]
        elif len(shap_values.shape) == 3:
            class_shap_values = shap_values[0, :, predicted_class_idx]
        else:
            class_shap_values = shap_values[0]
            
        # Explicitly define feature names matching the context output
        feature_names_raw = list(EXPECTED_COLUMNS) + ['engagement_index', 'motivation_score', 'behavior_stability']
        
        # Create a dictionary of feature -> shap_value
        feature_importance = {feature_names_raw[i]: float(class_shap_values[i]) for i in range(len(feature_names_raw))}
        
        # Sort by absolute magnitude to get top 6
        sorted_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:6]
        
        def clean_feature_name(name):
            name = name.replace("⁸", "").strip()
            if name == "engagement_index": return "Engagement Index"
            if name == "motivation_score": return "Motivation Score"
            if name == "behavior_stability": return "Behavior Stability"
            if name == "Email address": return "Contact Details"
            if "Name of the Student" in name: return "Student Identity"
            # Remove long parenthesis explanations
            if "(" in name: name = name.split("(")[0].strip()
            if "\n" in name: name = name.split("\n")[0].strip()
            return name

        shap_data = [{"feature": clean_feature_name(k), "value": v} for k, v in sorted_features]

        # Extract Student Name
        student_name = input_data.get("⁸Name of the Student", "Unknown")
        current_time = datetime.now().isoformat()

        # Compute behavior sentiment
        if behavior_label == 'Self- Motivated Learner' or behavior_label == 'Dependent Learner':
            behavior_sentiment = "+ve"
        else:
            behavior_sentiment = "-ve"

        # Save to database
        cursor.execute("""

        INSERT INTO predictions (
            student_name,
            timestamp,
            learning_prediction,
            behavior_prediction,
            behavior_sentiment,
            reward_score
        )

        VALUES (?, ?, ?, ?, ?, ?)

        """, (
            student_name,
            current_time,
            learning_label,
            behavior_label,
            behavior_sentiment,
            reward_score

        ))

        conn.commit()

        # Final Response
        return jsonify({

            "learning_speed_prediction": learning_label,

            "behavior_prediction": behavior_label,

            "behavior_sentiment": behavior_sentiment,

            "reward_score": reward_score,
            
            "recommendations": recommendations,
            
            "shap_data": shap_data

        })

    except Exception as e:

        return jsonify({

            "error": str(e)

        })

# HISTORY ROUTE
@app.route('/history', methods=['GET'])

def history():

    cursor.execute("""

    SELECT id, learning_prediction, behavior_prediction, behavior_sentiment, reward_score, student_name, timestamp FROM predictions

    ORDER BY id DESC

    """)

    rows = cursor.fetchall()

    history_data = []

    for row in rows:
        behavior_pred = row[2]
        behavior_sent = row[3]
        
        # Fallback for older database entries that don't have behavior_sentiment stored
        if not behavior_sent:
            if behavior_pred == 'Self- Motivated Learner' or behavior_pred == 'Dependent Learner':
                behavior_sent = "+ve"
            else:
                behavior_sent = "-ve"
                
        history_data.append({
            "id": row[0],
            "learning_prediction": row[1],
            "behavior_prediction": behavior_pred,
            "behavior_sentiment": behavior_sent,
            "reward_score": row[4],
            "student_name": row[5] if row[5] else "Unknown",
            "timestamp": row[6] if row[6] else ""
        })

    return jsonify(history_data)

@app.route('/history_page')
def history_page():
    return render_template("history.html")

@app.route('/about')
def about_page():
    return render_template("about.html")

@app.route('/contact')
def contact_page():
    return render_template("contact.html")

@app.route('/result')
def result_page():
    return render_template("result.html")

@app.route('/delete_history/<int:pred_id>', methods=['DELETE'])
def delete_history(pred_id):
    try:
        cursor.execute("DELETE FROM predictions WHERE id = ?", (pred_id,))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/delete_history_bulk', methods=['POST'])
def delete_history_bulk():
    try:
        data = request.json or {}
        ids = data.get("ids", [])
        if ids:
            placeholders = ",".join("?" for _ in ids)
            cursor.execute(f"DELETE FROM predictions WHERE id IN ({placeholders})", tuple(ids))
        else:
            cursor.execute("DELETE FROM predictions")
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload_page')
def upload_page():
    return render_template("upload.html")

@app.route('/upload_file')
def upload_file_page():
    return render_template("upload_file.html")

@app.route('/upload', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        filename = file.filename.lower()
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({"error": "Please upload a valid CSV or Excel file (.csv, .xlsx, .xls)"}), 400
        
        if len(df) == 0:
            return jsonify({"error": "The uploaded file is empty"}), 400
            
        # Extract columns dynamically
        name_col = None
        for col in df.columns:
            if 'name' in str(col).strip().lower():
                name_col = col
                break
                
        course_col = None
        for col in df.columns:
            if 'program' in str(col).strip().lower() or 'course' in str(col).strip().lower():
                course_col = col
                break
                
        sem_col = None
        for col in df.columns:
            if 'semester' in str(col).strip().lower() or 'sem' in str(col).strip().lower():
                sem_col = col
                break
                
        # Predict batch
        learning_labels, behavior_labels, reward_scores = predict_batch(df)
        
        results = []
        for i in range(len(df)):
            name = str(df.iloc[i][name_col]) if name_col else f"Student {i+1}"
            course = str(df.iloc[i][course_col]) if course_col else "Unknown"
            semester = str(df.iloc[i][sem_col]) if sem_col else "Unknown"
            
            name = name.strip() if isinstance(name, str) else f"Student {i+1}"
            
            behavior_pred = behavior_labels[i]
            if behavior_pred == 'Self- Motivated Learner':
                behavior_sentiment = "+ve"
            elif behavior_pred == 'Dependent Learner':
                behavior_sentiment = "+ve"
            else:
                behavior_sentiment = "-ve"
                
            results.append({
                "student_name": name,
                "program_course": course,
                "semester": semester,
                "learning_prediction": learning_labels[i],
                "behavior_prediction": behavior_pred,
                "behavior_sentiment": behavior_sentiment,
                "reward_score": float(reward_scores[i])
            })
            
        # Sort results by reward score descending
        sorted_results = sorted(results, key=lambda x: x['reward_score'], reverse=True)
        
        # Slice top 30
        top_30 = sorted_results[:30]
        
        # Generate complete Excel sheet of all processed records
        df_excel = pd.DataFrame(sorted_results)
        df_excel.columns = [
            'Student Name', 'Program / Course', 'Semester', 
            'Learning Speed Category', 'Behavior Category', 
            'Behavior Sentiment (+ve/-ve)', 'Reward Score'
        ]
        
        batch_id = str(uuid.uuid4())
        excel_filename = f"{batch_id}.xlsx"
        excel_path = os.path.join(EXPORTS_DIR, excel_filename)
        df_excel.to_excel(excel_path, index=False, engine='openpyxl')
        
        return jsonify({
            "success": True,
            "total_students": len(results),
            "top_30": top_30,
            "download_url": f"/download_excel/{batch_id}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_excel/<batch_id>')
def download_excel(batch_id):
    try:
        filename = f"{secure_filename(batch_id)}.xlsx"
        return send_from_directory(EXPORTS_DIR, filename, as_attachment=True, download_name="Student_Batch_Report.xlsx")
    except Exception as e:
        return f"Error downloading report: {str(e)}", 404


# RUN APP
if __name__ == '__main__':

    app.run(debug=True)