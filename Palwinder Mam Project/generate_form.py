import json

# Group definitions with exact column names and user-friendly labels
groups = [
    {
        "name": "Demographic / Personal",
        "fields": [
            ("⁸Name of the Student", "Name of the Student"),
            ("Gender", "Gender"),
            ("Age", "Age"),
            ("Nationality", "Nationality"),
            ("Religion", "Religion"),
            ("Food Preference", "Food Preference")
        ]
    },
    {
        "name": "Academic / Institutional",
        "fields": [
            ("Admission Year", "Admission Year"),
            ("Program / Course", "Program / Course"),
            ("Semester", "Semester"),
            ("Duration of the Couse (In years )", "Duration of Course"),
            ("Current Attendance Percentage (Overall)", "Current Attendance Percentage"),
            ("Previous Class Percentage (In percentage)", "Previous Class Percentage"),
            ("Skill", "Skill"),
            ("Total Hours of Class in One Week (In Hours)", "Total Hours of Class in One Week"),
            ("Special Education needs depending on the disability", "Special Education Needs"),
            ("University Name / Board Name", "University Name / Board Name"),
            ("Level of difficulty of subjects", "Level of difficulty of subjects")
        ]
    },
    {
        "name": "Behavioral Parameters (Part 1)",
        "fields": [
            ("Study Time in One Day(In Hours)", "Study Time in One Day"),
            ("Play Time in One Day (In Hours)", "Play Time in One Day"),
            ("Free Time in One Day(In Hours)", "Free Time in One Day"),
            ("Stress Level", "Stress Level"),
            ("Socializing with Friends", "Socializing with Friends"),
            ("Hours of Sleep (In hours)", "Hours of Sleep"),
            ("Interest in class subjects (Tell subject name in which you are interested), \nIf yes( write the subject name) , If no (write no)", "Interest in Class Subjects"),
            ("Test Anxiety", "Test Anxiety"),
            ("Critical Thinking", "Critical Thinking"),
            ("Studying in group", "Studying in Group"),
            ("Extra Time Utilization (In Hours)", "Extra Time Utilization"),
            ("Way of Homework", "Way of Homework"),
            ("Timely Submission of Assignments and Homework", "Timely Submission of Assignments and"),
            ("Class Participation Frequency", "Class Participation Frequency"),
            ("Discipline History", "Discipline History")
        ]
    },
    {
        "name": "Behavioral Parameters (Part 2)",
        "fields": [
            ("Note-taking Habits", "Note-taking Habits"),
            ("Absenteeism History", "Absenteeism History"),
            ("Peer Interactions", "Peer Interactions"),
            ("Number of Friends", "Number of Friends"),
            ("Participation in Group Activities", "Participation in Group Activities"),
            ("Response to Feedback / Criticism", "Response to Feedback / Criticism"),
            ("Question-Asking Frequency", "Question-Asking Frequency"),
            ("Help-Seeking Behavior", "Help-Seeking Behavior"),
            ("Leadership Roles", "Leadership Roles"),
            ("Sports Involvement", "Sports Involvement"),
            ("Volunteer Activities", "Volunteer Activities"),
            ("Level of Boredom During Classes", "Level of Boredom During Classes"),
            ("Having a Personal Tutor or go for Tuition?", "Having a Personal Tutor / Tuition"),
            ("Contents of the Course are Interesting", "Contents of the Course are Interesting"),
            ("Enjoy Mobile Devices for Learning", "Enjoy Mobile Devices for Learning"),
            ("Time Spent on Social Media (In Hours)", "Time Spent on Social Media")
        ]
    },
    {
        "name": "Family & Socio-Economic",
        "fields": [
            ("Parental Encouragement", "Parental Encouragement"),
            ("Living with Parents, Hostel or PG", "Living with Parents / Hostel / PG"),
            ("Living City or Location", "Living City or Location"),
            ("Family Size", "Family Size"),
            ("Family Income Level (Low (₹1.5 lakh to ₹4 lakh)/ Medium (₹4 lakh to ₹20 lakh) / High (>₹15 lakh))", "Family Income Level"),
            ("Mother's level of Education", "Mother's Level of Education"),
            ("Father's level of Education", "Father's Level of Education"),
            ("Father Career", "Father Career"),
            ("Mother Career", "Mother Career"),
            ("Parent Status", "Parent Status"),
            ("No of Brothers/ Sisters", "Number of Brothers / Sisters"),
            ("Position as child", "Position as Child")
        ]
    },
    {
        "name": "Health & Logistics",
        "fields": [
            ("Health Status", "Health Status"),
            ("Transport method used", "Transport Method Used"),
            ("Distance of Educational Institution (In KM.)", "Distance of Educational Institution"),
            ("Write Name if having any Physical Disability or Suffering a Critical Issue", "Write Name if having any Physical Disability")
        ]
    }
]

import re

def safe_id(name):
    s = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
    return s.strip('_')

html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASB-IRL Student Prediction System - Form</title>
    <!-- Bootstrap -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <!-- AOS Animation -->
    <link href="https://unpkg.com/aos@2.3.4/dist/aos.css" rel="stylesheet">
    <!-- CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <style>
        .form-section { padding-top: 100px; padding-bottom: 100px; }
        .form-container { max-width: 900px; margin: 0 auto; }
        .form-label { color: #fff; font-size: 0.9rem; margin-bottom: 0.2rem; }
    </style>
</head>
<body>
    <!-- NAVBAR -->
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top custom-nav">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">CASB-IRL</a>
        </div>
    </nav>

    <!-- FORM SECTION -->
    <section class="form-section" id="formSection">
        <div class="container">
            <div class="form-container">
                <!-- Progress -->
                <div class="progress mb-4">
                    <div class="progress-bar" id="progressBar" style="width:0%"></div>
                </div>
"""

js_mapping = []
js_validation = []

for i, group in enumerate(groups):
    active_class = "active" if i == 0 else ""
    html += f'\n                <!-- STEP {i+1} -->\n'
    html += f'                <div class="form-step {active_class}">\n'
    html += f'                    <h2 class="mb-4">{group["name"]}</h2>\n'
    html += f'                    <div class="row">\n'
    
    for exact_name, display_name in group["fields"]:
        input_id = safe_id(display_name)
        
        js_mapping.append(f'                {json.dumps(exact_name)}: document.getElementById("{input_id}").value')
        
        html += f'                        <div class="col-md-6 mb-3">\n'
        html += f'                            <label class="form-label">{display_name}</label>\n'
        if display_name == "Gender":
            html += f'                            <select class="form-control" id="{input_id}">\n'
            html += f'                                <option value="">Select Gender</option>\n'
            html += f'                                <option value="Male">Male</option>\n'
            html += f'                                <option value="Female">Female</option>\n'
            html += f'                            </select>\n'
        elif display_name == "Stress Level":
            html += f'                            <select class="form-control" id="{input_id}">\n'
            html += f'                                <option value="">Select Stress Level</option>\n'
            html += f'                                <option value="No Stress">No Stress</option>\n'
            html += f'                                <option value="Mild Stress">Mild Stress</option>\n'
            html += f'                                <option value="Severe Stress">Severe Stress</option>\n'
            html += f'                            </select>\n'
        else:
            # We'll just use text inputs for everything else to save space, backend robust handling will take care of unknown inputs.
            html += f'                            <input type="text" class="form-control" id="{input_id}" placeholder="Enter {display_name}">\n'
        html += f'                        </div>\n'
    
    html += f'                    </div>\n'
    html += f'                    <div class="mt-3">\n'
    if i > 0:
        html += f'                        <button class="btn prev-btn me-2" onclick="prevStep()">Previous</button>\n'
    if i < len(groups) - 1:
        html += f'                        <button class="btn next-btn" onclick="nextStep()">Next</button>\n'
    else:
        html += f'                        <button class="btn submit-btn" onclick="submitForm()">Predict</button>\n'
    html += f'                    </div>\n'
    html += f'                </div>\n'

html += """
                <!-- LOADING -->
                <div id="loadingBox" class="text-center mt-4" style="display: none;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Analyzing student profile...</p>
                </div>

                <!-- RESULT -->
                <div class="result-box mt-5" id="resultBox" style="display:none;">
                    <h2>Prediction Result</h2>
                    <div class="result-card text-center">
                        <h4 id="learningResult" class="text-info mb-3"></h4>
                        <h4 id="behaviorResult" class="text-warning mb-3"></h4>
                        <h4 id="rewardResult" class="text-success"></h4>
                    </div>
                </div>

            </div>
        </div>
    </section>

    <!-- JS -->
    <script src="https://unpkg.com/aos@2.3.4/dist/aos.js"></script>
    <script>
        AOS.init();

        let currentStep = 0;
        const steps = document.querySelectorAll(".form-step");

        function updateProgress() {
            const progress = ((currentStep + 1) / steps.length) * 100;
            document.getElementById("progressBar").style.width = progress + "%";
        }
        
        // Initialize progress bar
        updateProgress();

        function nextStep() {
            steps[currentStep].classList.remove("active");
            currentStep++;
            steps[currentStep].classList.add("active");
            updateProgress();
            window.scrollTo({ top: document.getElementById('formSection').offsetTop - 50, behavior: 'smooth' });
        }

        function prevStep() {
            steps[currentStep].classList.remove("active");
            currentStep--;
            steps[currentStep].classList.add("active");
            updateProgress();
            window.scrollTo({ top: document.getElementById('formSection').offsetTop - 50, behavior: 'smooth' });
        }

        async function submitForm() {
            const data = {
"""
html += ",\n".join(js_mapping)
html += """
            };

            // Optional: Form validation to ensure all fields are filled. 
            // In a huge form, users might miss fields. The backend handles empty string as "Unknown", 
            // but let's prompt them just in case, or we can relax it since it's 64 fields.
            // Let's relax validation since backend handles missing!
            
            document.getElementById("loadingBox").style.display = "block";
            document.getElementById("resultBox").style.display = "none";

            try {
                const response = await fetch("/predict", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                document.getElementById("loadingBox").style.display = "none";
                document.getElementById("resultBox").style.display = "block";

                if (result.error) {
                    document.getElementById("learningResult").innerHTML = "Error: " + result.error;
                    document.getElementById("behaviorResult").innerHTML = "";
                    document.getElementById("rewardResult").innerHTML = "";
                    return;
                }

                document.getElementById("learningResult").innerHTML = "Learning Speed: <strong>" + result.learning_speed_prediction + "</strong>";
                document.getElementById("behaviorResult").innerHTML = "Behavior: <strong>" + result.behavior_prediction + "</strong>";
                document.getElementById("rewardResult").innerHTML = "Reward Score: <strong>" + parseFloat(result.reward_score).toFixed(4) + "</strong>";
            } catch (e) {
                document.getElementById("loadingBox").style.display = "none";
                alert("An error occurred: " + e.message);
            }
        }
    </script>
</body>
</html>
"""

with open(r"c:\Users\Sudhanshu Gandhi\Desktop\Palwinder Mam Project\templates\form.html", "w", encoding="utf-8") as f:
    f.write(html)

print("form.html has been generated successfully.")
