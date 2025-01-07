from flask import Flask, render_template, request, flash
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client["psychometric_test_db"]
collection = db["results"]
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flashing messages

# Define questions and their options
questions = {
    "Usage Patterns": [
        {"id": "q1", "question": "On average, how much time do you spend on social media daily?", "options": ["A. Less than 1 hour", "B. 1-3 hours", "C. 4-6 hours", "D. More than 6 hours"]},
        {"id": "q2", "question": "What is the primary reason you use social media?", "options": ["A. Communication", "B. Entertainment", "C. Work/Business", "D. Information"]},
        {"id": "q3", "question": "How often do you check social media as soon as you wake up?", "options": ["A. Rarely", "B. Occasionally", "C. Frequently", "D. Always"]}
    ],
    "Psychological Impact": [
        {"id": "q4", "question": "Do you feel anxious or restless when you cannot access social media?", "options": ["A. Never", "B. Sometimes", "C. Often", "D. Always"]},
        {"id": "q5", "question": "How often do you compare your life to others on social media?", "options": ["A. Never", "B. Occasionally", "C. Frequently", "D. Always"]},
        {"id": "q6", "question": "Does social media usage affect your self-esteem or self-worth?", "options": ["A. Not at all", "B. Slightly", "C. Moderately", "D. Significantly"]}
    ],
    "Behavioral Impact": [
        {"id": "q7", "question": "Has your social media usage reduced the time spent on productive tasks?", "options": ["A. Never", "B. Occasionally", "C. Frequently", "D. Always"]},
        {"id": "q8", "question": "Do you feel distracted during work/study due to social media notifications?", "options": ["A. Rarely", "B. Sometimes", "C. Often", "D. Always"]},
        {"id": "q9", "question": "Has social media negatively impacted your relationships?", "options": ["A. Never", "B. Slightly", "C. Moderately", "D. Significantly"]}
    ],
    "Addiction Indicators": [
        {"id": "q10", "question": "How difficult do you find it to reduce your social media usage?", "options": ["A. Not difficult", "B. Slightly difficult", "C. Moderately difficult", "D. Extremely difficult"]},
        {"id": "q11", "question": "Have you tried to quit or reduce social media usage but failed?", "options": ["A. Never", "B. Once", "C. A few times", "D. Often"]},
        {"id": "q12", "question": "Do you often lose track of time while using social media?", "options": ["A. Never", "B. Occasionally", "C. Frequently", "D. Always"]}
    ],
}

score_mapping = {"A": 1, "B": 2, "C": 3, "D": 4}

@app.route('/')
def home():
    return render_template('index.html')  # If you have an index.html page

@app.route("/form", methods=["GET", "POST"])
def social_media_test():
    if request.method == "POST":
        # Collect responses and calculate section-wise scores
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        age = request.form.get('age')

        # Check for duplicate email
        if collection.find_one({"email": email}):
            flash("Duplicate Email ID! A record with this email already exists.", "error")
            return render_template("form.html", questions=questions)
        

        section_scores = {}
        total_score = 0

        for section, section_questions in questions.items():
            section_score = 0
            for q in section_questions:
                answer = request.form.get(q["id"])
                if answer:
                    section_score += score_mapping[answer]
            section_scores[section] = section_score
            total_score += section_score

        # Interpret the total score
        if total_score <= 20:
            result = "Low Usage: Minimal impact on daily life."
        elif 21 <= total_score <= 35:
            result = "Moderate Usage: Some impact; self-regulation may be needed."
        elif 36 <= total_score <= 50:
            result = "High Usage: Significant impact; may require intervention."
        else:
            result = "Addiction Indicators: High scores indicate potential social media addiction."

        # Save data to MongoDB
        document = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "age": int(age) if age.isdigit() else None,
            "section_scores": section_scores,
            "total_score": total_score,
            "result": result
        }
        collection.insert_one(document)

        return render_template('result.html', 
                               first_name=first_name, 
                               last_name=last_name, 
                               email=email, 
                               age=age, 
                               total_score=total_score, 
                               result=result, 
                               section_scores=section_scores)

    return render_template("form.html", questions=questions)

if __name__ == "__main__":
    app.run(debug=True)
