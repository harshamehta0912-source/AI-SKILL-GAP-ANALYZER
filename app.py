from flask import Flask, render_template, request,send_file
from reportlab.pdfgen import canvas
import sqlite3
import os

app = Flask(__name__)

print("DOWNLOAD ROUTE LOADED")

role_skills = {
    "data analyst": ["excel", "sql", "python", "power bi"],

    "production engineer": [
        "lean manufacturing",
        "autocad",
        "quality control",
        "problem solving"
    ],

    "quality engineer": [
        "quality control",
        "six sigma",
        "excel",
        "inspection"
    ],

    "maintenance engineer": [
        "plc",
        "electrical",
        "mechanical",
        "troubleshooting"
    ],

    "manufacturing engineer": [
        "cad",
        "lean manufacturing",
        "process improvement",
        "automation"
    ],

    "process engineer": [
        "process optimization",
        "excel",
        "quality control",
        "data analysis"
    ],

    "industrial engineer": [
        "lean manufacturing",
        "time study",
        "excel",
        "process improvement"
    ],

    "machine operator": [
        "machine handling",
        "safety",
        "quality control"
    ],

    "cnc operator": [
        "cnc programming",
        "g-code",
        "machine handling"
    ],

    "safety officer": [
        "osha",
        "risk assessment",
        "safety",
        "first aid"
    ]
}

course_suggestions = {
    "excel": "Excel for Data Analysis (YouTube / Coursera)",
    "sql": "SQL Bootcamp (Udemy)",
    "python": "Python for Everybody (Coursera)",
    "power bi": "Power BI Dashboard Course",
    "javascript": "JavaScript Basics (freeCodeCamp)",
    "git": "Git & GitHub Tutorial",
    "dsa": "DSA Practice (LeetCode)",
    "problem solving": "Problem Solving Basics",
    "mathematics": "Engineering Maths Revision",
    "cad": "AutoCAD Basics Course",
    "lean manufacturing": "Lean Manufacturing Fundamentals",
"quality control": "Quality Control Basics",
"six sigma": "Six Sigma Yellow Belt",
"inspection": "Quality Inspection Training",
"plc": "PLC Programming Basics",
"electrical": "Industrial Electrical Systems",
"mechanical": "Mechanical Maintenance Basics",
"troubleshooting": "Industrial Troubleshooting Course",
"process improvement": "Process Improvement Techniques",
"automation": "Industrial Automation Basics",
"process optimization": "Process Optimization Fundamentals",
"data analysis": "Data Analysis for Engineers",
"time study": "Time and Motion Study",
"machine handling": "Machine Operation Training",
"safety": "Industrial Safety Course",
"cnc programming": "CNC Programming Basics",
"g-code": "G-Code Programming",
"osha": "OSHA Workplace Safety",
"risk assessment": "Risk Assessment Training",
"first aid": "First Aid Certification"
}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    name = request.form.get("name")
    role = request.form.get("role").lower()

    skills = [skill.strip() for skill in request.form.get("skills").lower().split(",")]

    required = role_skills.get(role, [])
    missing = [s for s in required if s not in skills]
    suggestions = [course_suggestions.get(m, "No suggestion") for m in missing]

    score = int(((len(required) - len(missing)) / len(required)) * 100) if required else 0

    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM employees WHERE name=? AND role=?",
        (name, role.title())
    )

    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "UPDATE employees SET score=? WHERE name=? AND role=?",
            (score, name, role.title())
        )
    else:
        cursor.execute(
            "INSERT INTO employees (name, role, score) VALUES (?, ?, ?)",
            (name, role.title(), score)
        )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        name=name,
        role=role.title(),
        missing=missing,
        suggestions=suggestions,
        score=score
    )
@app.route("/download/<name>/<role>/<int:score>")
def download(name, role, score):

    filename = f"{name}_Skill_Report.pdf"

    c = canvas.Canvas(filename)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(150, 800, "AI Skill Gap Report")

    c.setFont("Helvetica", 14)
    c.drawString(50, 740, f"Employee Name: {name}")
    c.drawString(50, 710, f"Job Role: {role}")
    c.drawString(50, 680, f"Skill Match Score: {score}%")

    c.save()

    return send_file(filename, as_attachment=True)  
 
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees ORDER BY score DESC")
    employees = cursor.fetchall()

    names = [row[1] for row in employees]
    scores = [row[3] for row in employees]

    conn.close()

 
    return render_template(
        "dashboard.html",
        employees=employees,
        names=names,
        scores=scores
    )


if __name__ == "__main__":
    app.run(debug=True)
    
